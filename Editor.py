#!/usr/bin/env python
## editor subclassed from styledtextctrl

import wx
import wx.stc
import sys
import re
import atd
import SpellCheckerWindow
import MessageSystem
import os


# english defaults for verify, check
verify_token = "verify"
check_token = "check"
action_token = "action"

# pre-compile and cache regular expression patterns for use later
pattern_line_comments = re.compile("//.*")
pattern_block_comments = re.compile("/\*.*?\*/", flags=re.S)
pattern_double_quotes = re.compile("\".+?\"", flags=re.S)
pattern_single_quotes = re.compile("\'.*?\'", flags=re.S)
pattern_escape_quotes = re.compile(r"\\'", flags=re.S)
pattern_enclosure = re.compile("\n\s*\{")
pattern_object = re.compile("\+*\s*([a-zA-Z]*):")
pattern_classes = re.compile(": ([\w*|,|\s])*")


class ColorSchemer:

    def __init__(self):

        ## constructor for ColorSchemer, set default colors and fonts
        font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        font.SetNoAntiAliasing(False)
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

    def __init__(self, tads_classes, parent, notebook, style=wx.SIMPLE_BORDER):

        ## Constructor
        wx.stc.StyledTextCtrl.__init__(self, parent=parent, style=style)

        # default filename is "untitled", no default path
        self.filename = "untitled"
        self.path = ""

        # context sensitive help reference
        self.classes = tads_classes
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
        self.Bind(wx.stc.EVT_STC_AUTOCOMP_SELECTION, self.auto_code_selected)

        # reference to notebook
        self.notebook = notebook

    def on_char_added(self, event):

        # don't add if we're in string or comment
        anchor_at_style = self.GetStyleAt(self.GetAnchor())
        if check_for_plain_style(anchor_at_style) is False:
            return

        # when char is added, handle autoindent
        if event.GetKey() == 10:
            self.auto_indent()

        # when bracket is added, autoadd matching close bracket
        if event.GetKey() == 123:
            self.add_brackets()

        # when quotes added, autoadd quotes
        if event.GetKey() == 34:
            self.add_double_quotes()

        # handle autocompletion too
        self.auto_complete()

    def auto_code_selected(self, event):

        # we've selected an auto completion expression! under certain conditions,
        # we may choose to code templates
        selection = event.GetText()
        position = self.GetAnchor()

        # for when we insert anything ending in the word "Desc" add double quotes
        if selection[-4:] == "Desc":
            self.InsertText(position, " = \"\"")

        # for when we insert anything ending in the word "Msg" add single quotes
        if selection[-3:] == "Msg":
            self.InsertText(position, " = \'\'")

        # regions
        if selection == "regions":
            self.InsertText(position, " = [  ]")

        # for define indirect action
        if "DefineIAction" in selection:

            self.InsertText(position, self.insert_indent(1) + "execAction(cmd)" + self.insert_indent(1) +
                            "{" + self.insert_indent(2) + "\"{You} can't do that now. \";" +
                            self.insert_indent(1) + "}" + self.insert_indent(0) + ";")

        # for T action
        if "DefineTAction" in selection:
            self.InsertText(position, self.insert_indent(0) + ";")

        # for TI action
        if "DefineTIAction" in selection:
            self.InsertText(position, self.insert_indent(0) + ";")

        # for new verb rules
        if "VerbRule" in selection:

            self.InsertText(position, self.insert_indent(1) + "'verb'"
                            + self.insert_indent(1) + ": VerbProduction"
                            + self.insert_indent(1) + "action = Verb"
                            + self.insert_indent(1) + "verbPhrase = 'verb/verbing'"
                            + self.insert_indent(1) + "missingQ = 'what do you want to verb'"
                            + self.insert_indent(0) + ";")

    def insert_indent(self, level):

        # insert a number of indents * level

        indent = self.GetIndent()
        return_value = "\n"
        for i in range(level):
            for k in range(indent):
                return_value += " "
        return return_value

    def add_brackets(self):

        # add brackets to edited code
        position = self.GetAnchor()
        line = self.GetCurrentLine()
        self.InsertText(position, "\n\n}")
        self.SetLineIndentation(line, self.GetLineIndentation(line))
        self.SetLineIndentation(line + 1, self.GetLineIndentation(line) + self.GetIndent())
        self.SetLineIndentation(line + 2, self.GetLineIndentation(line))

    def add_double_quotes(self):

        # add quotes to edited code
        position = self.GetAnchor()
        self.InsertText(position, "\"")

    def add_single_quotes(self):

        # add single quotes to edited code
        position = self.GetAnchor()
        self.InsertText(position, "'")

    def auto_indent(self):

        line = self.GetCurrentLine()
        self.SetLineIndentation(line, self.GetLineIndentation(line - 1))
        self.SetCurrentPos(self.GetLineIndentPosition(line))
        self.SetAnchor(self.GetLineIndentPosition(line))

    def handle_not_in_object(self):

        # when our cursor is not in an object, add a small subset of suggestions
        defaults = "DefineIAction(Verb)", "DefineTAction(Verb)", "DefineTIAction(Verb)", "VerbRule(Verb)", "class"
        current_word = self.get_full_word()
        return_value = ""
        for word in defaults:
            if current_word in word:
                return_value += word + "^"
        return return_value

    def auto_complete(self):

        # engine to analyze code suggest keywords
        # conducted in a series of stages

        # stage 1: clean the code to be used, so the parser doesn't get fouled by unneeded keywords
        code = self.Text[0:self.GetAnchor() - 1]
        code = clean_string(code)

        # stage 2: take the processed code (now a list, divided into lines and backwards) and find
        # the classes of the object we're editing, plus the present enclosures
        suggestions = self.build_suggestions(code)

        # stage 3: finally, gather context data from entered word
        # make string to send to the stc autocompletion box
        # note - separator betwixt keywords in final string is a ^
        present_word = self.get_word()
        if len(present_word) < 1:
            return
        if present_word is "=":
            return
        if len(suggestions) > 0:
            self.AutoCompShow(len(present_word), suggestions)
        else:
            self.AutoCompCancel()

    def build_suggestions(self, code):

        # build suggestions from the code passed above
        suggestions = ""
        lines = code.split("\n")
        enclosures = in_enclosure(lines)
        in_verify = verify_token in enclosures
        in_check = check_token in enclosures
        in_action = action_token in enclosures
        in_dobj = "dobjFor" in enclosures
        in_iobj = "iobjFor" in enclosures

        # with some context info collected, build a list of library info
        pre_return_list = []
        if in_dobj or in_iobj:
            if not in_verify and not in_check and not in_action:
                pre_return_list.append("preCond")
                pre_return_list.append(verify_token + "()")
                pre_return_list.append(check_token + "()")
                pre_return_list.append(action_token + "()")
                for entry in pre_return_list:
                    suggestions += entry + "^"
                return suggestions
            if in_verify:
                pre_return_list.append("logicalRank(rank, key);")
                pre_return_list.append("dangerous")
                pre_return_list.append("illogicalNow(msg, params);")
                pre_return_list.append("illogical(msg, params);")
                pre_return_list.append("illogicalSelf(msg, params);")
                pre_return_list.append("nonObvious")
                pre_return_list.append("inaccessible(msg, params);")
        inherits = find_object(lines, self.notebook.objects)
        if inherits:
            check_on_line = self.get_line_suggestions(lines[-2], inherits)
            if check_on_line is not None:
                return check_on_line
            for i in inherits:
                for c in self.classes:
                    if i == c.name:
                        for m in c.members:
                            pre_return_list.append(m.name)
        else:
            # we're not editing an object, so provide the verb creation options if no indent is set
            if self.GetLineIndentation(self.GetCurrentLine()) == 0:
                return self.handle_not_in_object()

        # apply object listing first
        for o in self.notebook.objects:
            pre_return_list.append(o.name)

        # finalize for return
        pre_return_list = list(set(pre_return_list))
        pre_return_list = filter_suggestions(self.get_word(), pre_return_list)
        pre_return_list.sort()
        for entry in pre_return_list:
            suggestions += entry + "^"
        return suggestions

    def get_line_suggestions(self, line, inherits):

        # recommend remap options for dobj and iobj
        return_list = []
        if "dobj" in line:
            for c in self.classes:
                for i in inherits:
                    if c.name == i:
                        for m in c.members:
                            if "asDobjFor" in m.name:
                                return_list.append(m.name)
        if "iobjFor" in line:
            for c in self.classes:
                for i in inherits:
                    if c.name == i:
                        for m in c.members:
                            if "asIobjFor" in m.name:
                                return_list.append(m.name)
        if ":" in line:
            if self.GetLineIndentation(self.GetCurrentLine()) == 0:
                # we're probably editing an object, provide object inheritance suggestions
                for c in self.classes:
                    return_list.append(c.name)
        return_list = list(set(return_list))
        if len(return_list) < 1:
            return None
        else:
            return_string = ""
            return_list = list(set(return_list))
            return_list = filter_suggestions(self.get_word(), return_list)
            return_list.sort()
            for entry in return_list:
                return_string += entry + "^"
            return return_string

    def get_word(self):

        # return string of recently typed chars at the caret position
        anchor_position = self.GetAnchor() - 1
        if anchor_position >= len(self.Text):
            return ""
        for char_index in xrange(anchor_position, 1, -1):
            char = self.Text[char_index]
            if word_boundary(char):
                return self.Text[char_index + 1:anchor_position + 1].strip(".").strip()
        return ""

    def call_context_help(self, event):

        # get context sensitive help

        # start by getting the full word the caret is on top of
        search_string = self.get_full_word()
        for c in self.classes:
            if search_string == c.name:
                MessageSystem.show_message(c.name + ": " + c.help)
                return

        # what else is the caret near? find object and classes
        code = self.Text[0:self.GetAnchor() - 1]
        code = clean_string(code)
        lines = code.split('\n')
        inherits = find_object(lines, self.notebook.objects)

        # search for help in classes matching the search string
        member = prep_member(search_string)
        if 'objFor' in member:
            MessageSystem.show_message("Action handling with: " + member)
            return
        if inherits:
            for i in inherits:
                for c in self.classes:
                    if c.name == i:
                        for m in c.members:
                            if member == prep_member(m.name):
                                MessageSystem.show_message(m.name + ": " + m.help)

    def get_full_word(self):

        # returns full word at caret position
        anchor_position = self.GetAnchor()
        if anchor_position >= len(self.Text):
            return ""
        for end_of_word in xrange(anchor_position, len(self.Text)):
            if word_boundary(self.Text[end_of_word]):
                for start_of_word in xrange(anchor_position, 1, -1):
                    get_char = self.Text[start_of_word - 1]
                    if word_boundary(get_char):
                        return self.Text[start_of_word:end_of_word].strip()
        return ""

    def save(self, path, filename):

        # save contents of editor to file
        try:
            f = open(path + "/" + filename, 'w')
            f.write("%s" % self.Text)
            f.close()
            self.filename = filename
            self.path = path
            return True
        except IOError, e:
            MessageSystem.error("Could not save file: " + e.filename, "File save failure")
            return False

    def extract_strings(self):

        # return strings in this editor, cleaned of html
        text = self.GetText()
        remove_patterns = pattern_block_comments, pattern_line_comments
        for pattern in remove_patterns:
            text = pattern.sub("", text)

        # temporarily remove escape quotes
        text = pattern_escape_quotes.sub("[&escape &goes &here]", text)

        # extract strings
        all_double_quotes_strings = pattern_double_quotes.findall(text)
        text = pattern_double_quotes.sub("", text)
        all_single_quotes_strings = pattern_single_quotes.findall(text)
        return_text = ""
        for string in all_double_quotes_strings:
            return_text += string.strip("\"") + "\n"
        for string in all_single_quotes_strings:
            return_text += string.strip("\'") + "\n"
        return_text = return_text.replace("[&escape &goes &here]", "\'")
        return return_text

    def search_for(self, text):

        # select text from anchor
        maxPos = len(self.Text)
        textLength = len(text)
        minPos = self.GetAnchor()
        location = self.FindText(minPos, maxPos, text)
        if location != -1:
            self.GotoPos(location)
            self.SetAnchor(location)
            self.SetCurrentPos(location + textLength)

    def replace_with(self, old, new):

        # replace one string within selection
        maxPos = len(self.Text)
        textLength = len(new)
        minPos = self.GetAnchor()
        location = self.FindText(minPos, maxPos, old)
        if location != -1:
            text = self.Text[location:]
            self.BeginUndoAction()
            text = text.replace(old, new, 1)
            self.EndUndoAction()
            self.Text = self.Text[:location] + text
            self.GotoPos(location)
            self.SetAnchor(location)
            self.SetCurrentPos(location + textLength)

    def replace_all_with(self, old, new):

        # select text from anchor
        maxPos = len(self.Text)
        textLength = len(new)
        minPos = self.GetAnchor()
        location = self.FindText(minPos, maxPos, old)
        if location != -1:
            self.BeginUndoAction()
            self.Text = self.Text.replace(old, new)
            self.EndUndoAction()
            self.GotoPos(location)
            self.SetAnchor(location)
            self.SetCurrentPos(location + textLength)

    def spellcheck(self, project):

        # pull strings from page and send to atd spellcheck service
        strings = self.extract_strings()
        errors = atd.checkDocument(strings, "TadsPad_" + self.notebook.project_name)

        # pull in ignored words from ignored.txt
        ignored_file = open(os.path.join(project.path, "ignore.txt"), 'rU')
        ignored_words = ignored_file.read().split("\n")
        ignored_file.close()
        for error in errors[:]:
            if error.string in ignored_words:
                errors.remove(error)

        # we now have a list of spelling errors, display to user
        if errors:
            speller = SpellCheckerWindow.SpellCheckWindow(errors, self, project)
            speller.Show()


def check_for_plain_style(style):

    # read the style the anchor is at and determine if we need autocomplete
    comments = 3
    single_strings = 9
    double_strings = 10
    if style in (comments, single_strings, double_strings):
        return False
    return True


def word_boundary(char):

    # check that the char passed is/isnot a word boundary
    # return true if word boundary
    # false otherwise

    if char.isspace():
        return True
    separators = '.', '[', ']', '{', '}', '(', ')'
    if char in separators:
        return True
    return False


def remove_bracketed_enclosures(code):

    # remove bracketed enclosures from passed string
    # also: trim string to the ; on first indentation position, we don't need the rest
    return_value = ""
    brackets = 0
    lines = code.split("\n")
    for line in reversed(lines):
        if '}' in line:
            brackets += 1
        if brackets == 0:
            return_value = line + "\n" + return_value
        if '{' in line:
            if brackets > 0:
                brackets -= 1
        if len(line) > 0:
            if line[0] == ';':
                return return_value

    return return_value


def filter_suggestions(token, suggestions):

    # filter a list of suggestions
    # remove words with in the filter out string
    return_value = []
    if suggestions is None:
        return return_value
    for word in suggestions:
        if token.lower() in word.lower():
            return_value.append(word)
    return return_value


def clean_string(code):

    # return a string of code with strings, quotes, and bracketed code removed

    # describe all patterns to remove
    remove_patterns = pattern_line_comments, pattern_block_comments, pattern_double_quotes, pattern_single_quotes

    # remove all matching patterns to produced a cleaned string, easy to search
    removed_strings = code
    removed_strings = removed_strings.replace("\\\"", "")
    removed_strings = removed_strings.replace("\\'", "")
    removed_strings = removed_strings.replace("\r", "\n")
    for pattern in remove_patterns:
        removed_strings = pattern.sub("", removed_strings)

    # remove bracketed enclosures
    # when on the return, the lines are reversed, for easier for loop searching
    removed_strings = pattern_enclosure.sub("{", removed_strings)
    removed_strings = remove_bracketed_enclosures(removed_strings)

    return removed_strings


def find_object_reference(line, object_list):

    # find obj reference on the line we're editing
    tokens = re.split('[{0}]'.format(re.escape(" [](){};")), line)
    the_object = tokens[-1].split(".")[0]
    if the_object:
        for o in object_list:
            if o.name == the_object:
                return o
    return None


def find_object(lines, object_list):

    # return the present mixins of the object we're editing, else return none

    # first - if we're on top of an object reference (ex: object.property) return those classes instead of the
    # master reference here
    top_line = lines[-2]
    if "." in top_line:
        object_reference = find_object_reference(top_line, object_list)
        if object_reference:
            return_value = []
            for c in object_reference.inherits:
                return_value.append(c)
            if len(return_value) > 0:
                return return_value
            else:
                return None

    for line in lines:

        obj = pattern_object.search(line)
        if obj:
            classes = pattern_classes.search(line)
            if classes:
                string_of_classes = classes.group()
                string_of_classes = string_of_classes.strip(":")
                list_of_classes = string_of_classes.split(",")
                if list_of_classes is not None:
                    return_value = []
                    for c in list_of_classes:
                        return_value.append(c.strip())
                    return return_value

    return None


def prep_member(member):

    # prepare member passed above for help system comparison
    string = member.strip()
    return_value = ''
    if 'objFor' in string:
        return string
    for c in string:
        if c is '(':
            break;
        return_value += c
    return return_value


def in_enclosure(lines):

    # check if we're in enclosures marked by each token in "args"
    # verify return value with syntax: if "token" in "return_value": then do this
    tokens = action_token, check_token, verify_token, "dobjFor", "iobjFor"
    return_value = ""
    for line in lines:
        for token in tokens:
            if token in line:
                if token is "dobjFor" or token is "iobjFor":
                    if "asDobjFor" not in line and "asIobjFor" not in line:
                        return_value = return_value + token + " "
                else:
                    return_value = return_value + token + " "
    return return_value

__author__ = 'dj'
