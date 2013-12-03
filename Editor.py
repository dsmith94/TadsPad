#!/usr/bin/env python
## editor subclassed from styledtextctrl

import wx
import wx.stc
import sys
import re
import ObjectBrowser
import MessageSystem


class ColorSchemer:

    def __init__(self):

        ## constructor for ColorSchemer, set default colors and fonts
        font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.face = font.GetFaceName()
        self.size = font.GetPointSize()
        self.color_list = dict()

        ## attempt to load default color config
        try:
            self.load_colors('default.conf')
        except IOError, e:
            MessageSystem.error("Could not locate file: " + e.filename + " - TadsPad will exit.", "Terminal failure")
            sys.exit(1)

    def load_colors(self, filename):

        ## load color settings from file
        f = open(filename, 'r')
        for line in f:
            parsed = line.split(' ', 1)
            if parsed[0] != "CARET":
                self.color_list.update({parsed[0]: parsed[1].strip("\n") + ",face:%s,size:%d," % (self.face, self.size)})
            else:
                self.color_list.update({parsed[0]: parsed[1].strip("\n")})
        f.close()

    def update_colors(self, ctrl):

        # set styles from our colors list dictionary
        ctrl.SetCaretForeground(self.color_list["CARET"])
        ctrl.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, self.color_list["LINENUMBER"])
        ctrl.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, self.color_list["DEFAULT"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_DEFAULT, self.color_list["DEFAULT"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_BLOCK_COMMENT, self.color_list["BLOCK_COMMENT"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_LINE_COMMENT, self.color_list["LINE_COMMENT"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_D_STRING, self.color_list["D_STRING"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_S_STRING, self.color_list["S_STRING"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_HTML_DEFAULT, self.color_list["HTML_DEFAULT"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_HTML_STRING, self.color_list["HTML_STRING"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_HTML_TAG, self.color_list["HTML_TAG"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_IDENTIFIER, self.color_list["IDENTIFIER"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_LIB_DIRECTIVE, self.color_list["LIB_DIRECTIVE"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_MSG_PARAM, self.color_list["MSG_PARAM"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_NUMBER, self.color_list["NUMBER"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_OPERATOR, self.color_list["OPERATOR"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_PREPROCESSOR, self.color_list["PREPROCESSOR"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_KEYWORD, self.color_list["KEYWORD"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_USER1, self.color_list["USER1"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_USER2, self.color_list["USER2"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_USER3, self.color_list["USER3"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_X_DEFAULT, self.color_list["X_DEFAULT"])
        ctrl.StyleSetSpec(wx.stc.STC_T3_X_STRING, self.color_list["X_STRING"])


class EditorCtrl(wx.stc.StyledTextCtrl):

    def __init__(self, help_dictionary, parent, auto_code_repo, style=wx.SIMPLE_BORDER):

        ## Constructor
        wx.stc.StyledTextCtrl.__init__(self, parent=parent, style=style)

        # default filename is "untitled", no default path
        self.filename = "untitled"
        self.path = ""

        # context sensitive help reference
        self.help = help_dictionary
        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.call_context_help)

        # autoindent system
        self.Bind(wx.stc.EVT_STC_CHARADDED, self.on_char_added)

        # set lexer to tads 3
        self.SetLexer(wx.stc.STC_LEX_TADS3)

        # default margin settings
        self.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        r = wx.Display().GetGeometry()
        self.SetMarginWidth(0, (r.Width / 30))

        ## set color scheme object
        self.color_scheme = ColorSchemer()
        self.color_scheme.update_colors(self)
        self.anchor_at_style = 0

        # indents
        self.SetIndent(4)
        self.SetUseTabs(0)

        ## is file saved? keep answer here
        self.saved = True

        ## autocompletion system setup
        self.AutoCompSetAutoHide(0)
        self.AutoCompSetSeparator(94)
        self.AutoCompSetDropRestOfWord(True)
        self.AutoCompSetIgnoreCase(1)
        self.auto_code_list = auto_code_repo
        self.Bind(wx.stc.EVT_STC_AUTOCOMP_SELECTION, self.auto_code_selected)

    def on_char_added(self, event):

        # when char is added, handle autoindent
        if event.GetKey() == 10:
            line = self.GetCurrentLine()
            self.SetLineIndentation(line, self.GetLineIndentation(line - 1))
            self.SetCurrentPos(self.GetLineIndentPosition(line))
            self.SetAnchor(self.GetLineIndentPosition(line))

        # handle autocompletion too
        self.prepare_auto_complete()

    def auto_code_selected(self, event):

        # we've selected an auto completion expression! under certain conditions,
        # we may choose to add brackets

        selection = event.GetText()
        if keyword_needs_brackets(selection):
            position = self.GetAnchor()
            line = self.GetCurrentLine()
            self.InsertText(position, "\n{\n\n}")
            self.SetLineIndentation(line + 1, self.GetLineIndentation(line))
            self.SetLineIndentation(line + 2, self.GetLineIndentation(line) + self.GetIndent())
            self.SetLineIndentation(line + 3, self.GetLineIndentation(line))

    def get_word(self):

        # return string of recently typed chars at the caret position
        anchor_position = self.GetAnchor() - 1
        if anchor_position >= len(self.Text):
            return ""
        for char_index in xrange(anchor_position, 1, -1):
            if self.Text[char_index] == '\n':
                return ""
            if self.Text[char_index].isspace() or self.Text[char_index] == ".":
                return self.Text[char_index:anchor_position].strip(".").strip()
        return ""

    def call_context_help(self, event):

        # get context sensitive help

        # start by getting the full word the caret is on top of
        search_string = self.get_full_word()
        if search_string != "":

            # isolate token from other chars that would confuse the help dictionary
            pattern = re.compile("\s*([\w|]*)\s?\(?")
            token = pattern.search(search_string)

            # show help if the returned token exists in dictionary
            if token is not None:
                search_string = token.group(0)
                if search_string != "":
                    if search_string in self.help:
                        MessageSystem.show_message(self.help[search_string])
            else:
                MessageSystem.show_message("")


    def get_full_word(self):

        # returns full word at caret position
        anchor_position = self.GetAnchor()
        if anchor_position >= len(self.Text):
            return ""
        for end_of_word in xrange(anchor_position, len(self.Text)):
            if self.Text[end_of_word].isspace() or self.Text[end_of_word] == '\n':
                for start_of_word in xrange(anchor_position, 1, -1):
                    if self.Text[start_of_word] == '\n' or self.Text[start_of_word].isspace():
                        return self.Text[start_of_word:end_of_word].strip()
        return ""

    def save(self, path, filename, object_browser):

        # save contents of editor to file
        try:
            f = open(path + "/" + filename, 'w')
            f.write("%s" % self.Text)
            f.close()
            self.filename = filename
            self.path = path
            object_browser.rebuild_object_catalog()
            return True
        except IOError, e:
            MessageSystem.error("Could not save file: " + e.filename, "File save failure")
            return False

    def show_code_completion_box(self, keywords, show_objects=True):

        # prepare the box by getting all the properties from a list of keywords

        # if we have no classes passed, terminate now
        if keywords == ';':
            return

        # first get complete list of game objects
        object_list = wx.GetTopLevelParent(self).object_browser.objects

        # if an object referenece is passed, get those object properties
        for o in object_list:
            if keywords[0] == o.definition:
                keywords = o.classes
                show_objects = False
                break

        # pull the present word that the caret is editing right now
        # if there's no word there, terminate
        present_word = self.get_word()
        if len(present_word) < 1:
            return

        # now scan the keywords passed above and prepare string to pass to the auto completion system
        string_of_keywords = ""
        for the_class in keywords:
            if the_class in self.auto_code_list:
                for the_property in self.auto_code_list[the_class].split('^'):
                    if the_property.find(present_word) > -1:
                        string_of_keywords += the_property + "^"

        # while we're at it, prepare a list of the objects we can enter as well
        # this gives autocompletion to tads game objects
        if show_objects is True:
            for o in object_list:
                if o.definition.find(present_word) > -1:
                    string_of_keywords += o.definition.strip() + "^"

        if string_of_keywords != "":
            self.AutoCompShow(len(present_word) + 1, string_of_keywords)

    def prepare_auto_complete(self):

        # only do autocomplete if style system (in the editor) says we're not in a string or comment
        # and check for recently edited object near caret
        if check_for_plain_style(self.anchor_at_style) is False:
            self.anchor_at_style = self.GetStyleAt(self.GetAnchor())
            return
        self.anchor_at_style = self.GetStyleAt(self.GetAnchor())
        if check_for_plain_style(self.anchor_at_style) is True:
            code_to_check = self.Text[0:self.GetAnchor() + 1]
            current_classes = analyze_code_context(code_to_check)
            self.show_code_completion_box(current_classes)


def check_for_plain_style(style):

    # read the style the anchor is at and determine if we need autocomplete
    comments = 3
    single_strings = 9
    double_strings = 10
    if style in (comments, single_strings, double_strings):
        return False
    return True


def analyze_code_context(code):

    # search the code backwards (from end to start) to find
    # which object (or otherwise) we're editing

    # return ; for no object, return classes for this object otherwise

    # split all lines for easier searching
    lines = remove_unused_strings(code)

    # on top of a comment, don't do anything
    first_line = lines[-1]
    if first_line.find("/*") > -1 or first_line.find("*/") > -1 or first_line.find("//") > -1:
        return ';'

    # do a couple of tests, only for the first line
    # and if we find an equal sign, bring out the default boolean values
    if first_line.find("=") > -1:
        return ["Boolean"]

    # no indent? then we probably have an object declaration
    if first_line.find(": ") > -1:
        if first_line[0].isspace() is False:
            return ["Classes"]

    # reference to object? then return that object
    if len(first_line) > 1:
        obj_reference = editing_object_reference(first_line)
        if obj_reference is not None:
            return [obj_reference]

    # otherwise, search code to find appropriate context
    for line in reversed(lines):

        if len(line) > 1:

            # if we find a ; at beginning of line, we're not in a object
            if line[0] == ';':
                return ';'

            # if we find one of the dobjFor or iobjFor's, show the objectfor macros
            if re.search("[d|i]objFor", line) > -1:
                return_value = ["ObjFor"]
                return return_value

            # if we find a "verify" command, return the verify macros
            if re.search("verify\s*\(\s*\)", line) > -1:
                return_value = ["Verify"]
                return return_value

            # if we find a "check" command, return the verify macros
            if re.search("check\s*\(\s*\)", line) > -1:
                return_value = ["Check"]
                return return_value

            # if we find an object definition, isolate its classes
            object_definition = re.search(ObjectBrowser.classes_look_like, line)
            if object_definition:
                return_value = []
                list_of_classes = object_definition.group(0).split(',')

                # now prepare a list of classes to return
                for value in list_of_classes:
                    return_value.append(value.strip(":").strip(' ').strip('\n').strip('\r').strip('\t'))

                return return_value

    # cover ourselves in case we don't find anything
    return ";"


def editing_object_reference(string):

    # return object if we're editing a reference to an object
    # no spaces, colons, semicolons, etc... allowed - return false then

    tokens = re.findall("[\w]+\.", string)
    if tokens:
        if tokens[-1].find('.') > -1:
            return tokens[-1][:tokens[-1].find('.')]
    return None


def keyword_needs_brackets(keyword):

    # return true if we're passed a keyword that gets brackets
    if keyword.find("dobjFor") > -1:
        return True
    if keyword.find("iobjFor") > -1:
        return True
    if keyword.find("verify()") > -1:
        return True
    if keyword.find("check()") > -1:
        return True
    if keyword.find("action()") > -1:
        return True
    return False


def remove_unused_strings(code):

    # return a string of code with strings, quotes, and bracketed code removed

    # remove comments
    removed_strings = code
    removed_strings = re.sub("//.*", "", removed_strings)
    removed_strings = re.sub("/\*.*?\*/", "", removed_strings, flags=re.S)

    # remove strings from code
    removed_strings = removed_strings.replace("\\\"", "")
    removed_strings = removed_strings.replace("\\'", "")
    removed_strings = re.sub("\".+?\"", "", removed_strings, flags=re.S)
    removed_strings = re.sub("\'.*?\'", "", removed_strings, flags=re.S)

    # split all lines for editing
    lines = removed_strings.strip().replace("\r", "").replace("\n{", "{").split("\n")
    return_value = []
    in_brackets = 0
    dont_add = 0
    for i in range(len(lines) - 1, 0, -1):
        if dont_add > 0:
            dont_add -= 1
        if lines[i].find("}") > -1:
            in_brackets += 1
        if lines[i].find("{") > -1:
            if in_brackets > 0:
                in_brackets -= 1
                dont_add = 3
        if in_brackets == 0 and dont_add == 0:
            return_value.insert(0, lines[i].strip("\r"))

    return filter(None, return_value)


__author__ = 'dj'
