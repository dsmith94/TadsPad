#!/usr/bin/env python
## editor subclassed from styledtextctrl

import wx
import wx.stc
import TClass
import re
import atd
import SpellCheckerWindow
import MessageSystem
import os
import xml.etree.ElementTree as ET

# english defaults for verify, check
verify_token = u"verify"
check_token = u"check"
action_token = u"action"
direct_token = u"dobjFor"
indirect_token = u"iobjFor"
remap_direct_token = u"asDobjFor"
remap_indirect_token = u"asIobjFor"
inObj_suggestions = "preCond", verify_token + "()", check_token + "()", action_token + "()"
verify_suggestions = ("logicalRank(rank, key);", "dangerous", "illogicalNow(msg, params);", "illogical(msg, params);",
                      "illogicalSelf(msg, params);", "nonObvious", "inaccessible(msg, params);")


# pre-compile and cache regular expression patterns for use later
pattern_line_comments = re.compile("//.*")
pattern_block_comments = re.compile("/\*.*?\*/", flags=re.S)
pattern_double_quotes = re.compile("\".+?\"", flags=re.S)
pattern_single_quotes = re.compile("\'.*?\'", flags=re.S)
pattern_escape_quotes = re.compile(r"\\'", flags=re.S)
pattern_enclosure = re.compile("\n\s*\{")
pattern_object = re.compile("\+*\s*([a-zA-Z]*):")
pattern_classes = re.compile(": ([\w*|,|\s])*")

# code analysis filter system
# use these presets to analyze a block of code for suggestions
analyzer = (verify_token, verify_suggestions, {'objects': None, 'self': None}), \
           (action_token, None, {'objects': None, 'self': None}), \
           (check_token, None, {'objects': None, 'self': None}), \
           (".", None, {'members': None}), (":", None, {'classes': None}), \
           ('@', None, {'objects': None}), \
           (direct_token, inObj_suggestions, {}), \
           (indirect_token, inObj_suggestions, {}), \
           (remap_direct_token, None, {'self': None, 'filter': [direct_token, indirect_token], 'prefix': 'as'})

# defaults when editing outside a template
outside_template = u"DefineIAction(Verb)", u"DefineTAction(Verb)", u"DefineTIAction(Verb)", u"VerbRule(Verb)", u"class"


class ColorSchemer:

    def __init__(self):

        # constructor for ColorSchemer, set default colors and fonts
        font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.face = font.GetFaceName()
        self.size = font.GetPointSize()
        self.colors = None

        # attempt to load default color config
        self.load_colors(os.path.join('themes', 'Obsidian.xml'))

    def load_colors(self, filename):

        # load color settings from xml file
        try:
            tree = ET.parse(filename)
            self.colors = tree.getroot()
        except IOError, e:
            MessageSystem.error("Could not locate file: " + e.filename, "Theme Change Unsuccessful")

    def update_colors(self, ctrl):

        # set styles from xml colors tree in memory
        color = wx.stc
        caret = [c.attrib['color'] for c in self.colors if c.tag == 'foreground']
        if caret:
            caret = caret[0]
        else:
            caret = 'BLACK'
        background = [c.attrib['color'] for c in self.colors if c.tag == 'background']
        if background:
            background = background[0]
        else:
            background = 'WHITE'
        foregrounds = dict()
        foregrounds[color.STC_STYLE_LINENUMBER] = 'lineNumber'
        foregrounds[color.STC_STYLE_DEFAULT] = 'foreground'
        foregrounds[color.STC_T3_DEFAULT] = 'foreground'
        foregrounds[color.STC_T3_X_DEFAULT] = 'foreground'
        foregrounds[color.STC_T3_KEYWORD] = 'keyword'
        foregrounds[color.STC_T3_BLOCK_COMMENT] = 'multiLineComment'
        foregrounds[color.STC_T3_LINE_COMMENT] = 'singleLineComment'
        foregrounds[color.STC_T3_HTML_STRING] = 'string'
        foregrounds[color.STC_T3_S_STRING] = 'string'
        foregrounds[color.STC_T3_D_STRING] = 'string'
        foregrounds[color.STC_T3_X_STRING] = 'string'
        foregrounds[color.STC_T3_HTML_STRING] = 'string'
        foregrounds[color.STC_SEL_LINES] = 'selectionForeground'
        foregrounds[color.STC_T3_HTML_DEFAULT] = 'class'
        foregrounds[color.STC_T3_HTML_TAG] = 'class'
        foregrounds[color.STC_T3_OPERATOR] = 'operator'
        foregrounds[color.STC_T3_MSG_PARAM] = 'operator'
        foregrounds[color.STC_T3_IDENTIFIER] = 'operator'
        foregrounds[color.STC_T3_NUMBER] = 'number'
        foregrounds[color.STC_T3_PREPROCESSOR] = 'constant'
        foregrounds[color.STC_T3_LIB_DIRECTIVE] = 'constant'
        for key, value in foregrounds.iteritems():
            for c in self.colors:
                weight = ''
                if key == color.STC_T3_BLOCK_COMMENT or key == color.STC_T3_LINE_COMMENT:
                    weight = ',italic'
                if key == color.STC_T3_KEYWORD:
                    weight = ',bold'
                if c.tag == value:
                    style = "fore:%s,back:%s,face:%s,size:%d%s" % (c.attrib['color'], background, self.face, self.size, weight)
                    ctrl.StyleSetSpec(key, style)
        ctrl.SetCaretForeground(caret)


class EditorCtrl(wx.stc.StyledTextCtrl):

    def __init__(self, parent, notebook, style=wx.SIMPLE_BORDER):

        ## Constructor
        wx.stc.StyledTextCtrl.__init__(self, parent=parent, style=style)

        # default filename is "untitled", no default path
        self.filename = "untitled"
        self.path = ""

        # context sensitive help reference
        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.call_context_help)

        # autoindent system
        self.Bind(wx.stc.EVT_STC_CHARADDED, self.on_char_added)

        # set lexer to tads 3
        self.SetLexer(wx.stc.STC_LEX_TADS3)
        self.SetKeyWords(0, "break case catch class case continue do default delete else enum finally for foreach function goto if intrinsic local modify new nil property replace return self switch throw token true try while")

        # default margin settings
        self.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        r = wx.Display().GetGeometry()
        self.SetMarginWidth(0, (r.Width / 30))

        ## set color scheme object
        self.scheme = ColorSchemer()

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
        if selection[-4:] == u"Desc":
            self.InsertText(position, u" = \"\"")

        # for when we insert anything ending in the word "Msg" add single quotes
        if selection[-3:] == u"Msg":
            self.InsertText(position, u" = \'\'")

        # regions
        if selection == u"regions":
            self.InsertText(position, u" = [  ]")

        # for define indirect action
        if u"DefineIAction" in selection:

            self.InsertText(position, self.insert_indent(1) + u"execAction(cmd)" + self.insert_indent(1) +
                            u"{" + self.insert_indent(2) + u"\"{You} can't do that now. \";" +
                            self.insert_indent(1) + u"}" + self.insert_indent(0) + ";")

        # for T action
        if u"DefineTAction" in selection:
            self.InsertText(position, self.insert_indent(0) + ";")

        # for TI action
        if u"DefineTIAction" in selection:
            self.InsertText(position, self.insert_indent(0) + ";")

        # for new verb rules
        if u"VerbRule" in selection:
            self.InsertText(position, self.insert_indent(1) + u"'verb'"
                            + self.insert_indent(1) + u": VerbProduction"
                            + self.insert_indent(1) + u"action = Verb"
                            + self.insert_indent(1) + u"verbPhrase = 'verb/verbing'"
                            + self.insert_indent(1) + u"missingQ = 'what do you want to verb'"
                            + self.insert_indent(0) + u";")

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

    def find_object_methods(self, line):

        # find object on a single line
        # return methods
        tokens = re.split('[{0}]'.format(re.escape(" [](){};")), line)
        obj = tokens[-1].split(".")[0]
        if obj:
            return [m.name for o in self.notebook.objects if o.name == obj for m in o.members if m.type != "method"]

    def find_object_template(self):

        # determine if caret is presently editing an object template
        # return object reference if true, None if false
        line_number = self.GetCurrentLine()
        objects = TClass.search(self.Text, 'object').values()
        for o in objects:
            TClass.get_all_members(o.name, self.notebook.classes)
            if line_number in range(o.line, o.end):
                return o

    def auto_complete(self):

        # engine to analyze code suggest keywords
        # conducted in a series of stages

        # stage 1: clean the code to be used, so the parser doesn't get fouled by unneeded keywords
        code = self.Text[0:self.GetAnchor() - 1]
        code = clean_string(code)

        # stage 2: take the processed code and find
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
        results = []
        full_line, caret = self.GetCurLine()
        context = search(code, full_line[:caret])
        template = self.find_object_template()
        print([g for g in self.notebook.classes['Room'].inherits])
        # analyze code based on present template and line in context
        for enclosure, suggestions, flags in analyzer:
            if enclosure in context:
                if suggestions:
                    results.extend(suggestions)
                if 'classes' in flags:
                    results = self.notebook.classes.keys()
                if 'members' in flags:
                    members = self.find_object_methods(full_line[:caret])
                    if members:
                        results = members
                if 'objects' in flags:
                    results.extend([o.name for o in self.notebook.objects])
                if 'self' in flags:
                    if template:
                        results.extend([m.name for m in template.members])
                if 'filter' in flags:
                    results = [r for f in flags['filter'] for r in results if f in r]
                if 'prefix' in flags:
                    results = [flags['prefix'] + r.title() for r in results]

        # still no results, figure out if we're in a object template
        if not results:
            if template:
                results.extend([m.name for m in template.members])
                results.extend([o.name for o in self.notebook.objects])
            else:
                results = outside_template

        # finalize for return
        results = list(set(results))
        results = filter_suggestions(self.get_word(), results)
        results.sort()
        return '^'.join(results)

    def get_word(self):

        # return string of recently typed chars at the caret position
        anchor_position = self.GetAnchor() - 1
        if anchor_position >= len(self.Text):
            return ""
        for char_index in xrange(anchor_position, 1, -1):
            char = self.Text[char_index]
            if word_boundary(char):
                return self.Text[char_index + 1:anchor_position + 1].strip(".").strip("@").strip()
        return ""

    def call_context_help(self, event):

        # get context sensitive help

        # print [m.name for m in self.notebook.classes["OutdoorRoom"].members]

        # start by getting the full word the caret is on top of
        search_string = self.get_full_word()
        for c in self.notebook.classes.values():
            if search_string == c.name:
                MessageSystem.show_message(c.name + ": " + c.help)
                return

        # search for help in classes matching the search string
        member = prep_member(search_string)
        if 'objFor' in member:
            MessageSystem.show_message("Action handling with: " + member)
            return

        # search current line for help data
        full_line, caret = self.GetCurLine()
        if '.' in full_line[:caret]:
            tokens = re.split('[{0}]'.format(re.escape(" [](){};")), full_line[:caret])
            the_object = tokens[-1].split(".")[0]
            if the_object:
                match = filter(lambda x: x.name == the_object, self.notebook.objects)
                if match:
                    if match.members:
                        [MessageSystem.show_message(m.name + ": " + m.help) for m in match.members
                         if member == prep_member(m.name)]

        # now search currently edited object
        line_number = self.GetCurrentLine()
        for o in self.notebook.objects:
            if line_number in range(o.line, o.end):
                for m in o.members:
                    if member == prep_member(m.name):
                        MessageSystem.show_message(m.name + ": " + m.help)
                        break

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


def search(code, line):

    # scan current code for possible enclosures we're in
    # look first in current line, then in all code
    # the order here is important, by the way
    if '@' in line:
        return '@'
    if ':' in line:
        return ':'
    if '.' in line:
        return '.'
    remaps = [t for t in [direct_token, indirect_token] if t in line]
    if remaps:
        return [remap_direct_token]
    tokens = verify_token, action_token, check_token, direct_token, indirect_token
    return [t for t in tokens if t in code]


__author__ = 'dj'
