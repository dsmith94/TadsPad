#!/usr/bin/env python
## editor subclassed from styledtextctrl

import wx
import wx.stc
import TadsParser
import re
import codecs
import atd
import SpellCheckerWindow
import MessageSystem
import os
import embedded
import xml.etree.ElementTree as ET

# english defaults for verify, check
verify_token = u"verify"
check_token = u"check"
action_token = u"action"
direct_token = u"dobjFor"
indirect_token = u"iobjFor"
remap_direct_token = u"asDobjFor"
remap_indirect_token = u"asIobjFor"
inObj_suggestions = u"preCond", verify_token + u"()", check_token + u"()", action_token + u"()"
verify_suggestions = (u"logicalRank(rank, key);", u"dangerous", u"illogicalNow(msg, params);", u"illogical(msg, params);",
                      u"illogicalSelf(msg, params);", u"nonObvious", u"inaccessible(msg, params);")

function_suggestions = (u"finishGameMsg(msg, extra)", u"finishGame()")
endgame_suggestions = (u"ftDeath", u"ftVictory")


# colors to tags list
text_styles = (("STC_STYLE_LINENUMBER", 'lineNumber'),
               ("STC_STYLE_DEFAULT", 'foreground'),
               ("STC_T3_DEFAULT", 'foreground'),
               ("STC_T3_X_DEFAULT", 'foreground'),
               ("STC_T3_KEYWORD", 'keyword'),
               ("STC_T3_BLOCK_COMMENT", 'multiLineComment'),
               ("STC_T3_LINE_COMMENT", 'singleLineComment'),
               ("STC_T3_HTML_STRING", 'string'),
               ("STC_T3_S_STRING", 'string'),
               ("STC_T3_D_STRING", 'string'),
               ("STC_T3_X_STRING", 'string'),
               ("STC_T3_HTML_STRING", 'string'),
               ("STC_SEL_LINES", 'selectionForeground'),
               ("STC_T3_HTML_DEFAULT", 'class'),
               ("STC_T3_HTML_TAG", 'class'),
               ("STC_T3_OPERATOR", 'operator'),
               ("STC_T3_MSG_PARAM", 'operator'),
               ("STC_T3_IDENTIFIER", 'operator'),
               ("STC_T3_NUMBER", 'number'),
               ("STC_T3_PREPROCESSOR", 'constant'),
               ("STC_T3_LIB_DIRECTIVE", 'constant'),
               ("STC_T3_BRACE", 'annotation'),
               ("STC_STYLE_BRACEBAD", 'searchResultIndication'),
               ("STC_STYLE_BRACELIGHT", 'staticMethod'))


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
# note the analyzer can be broken down into three parts:
# 1. the enclosure, 2. the suggestions for the enclosure, and 3. special flags for the enclosure
analyzer = (verify_token, verify_suggestions, ('objects', 'self')), \
           (action_token, None, ('objects', 'self')), \
           (check_token, None, ('objects', 'self')), \
           (".", None, 'members'), (":", None, 'classes'), \
           ('@', None, 'objects'), \
           (direct_token, inObj_suggestions, {}), \
           (indirect_token, inObj_suggestions, {}), \
           (remap_direct_token, None, {'self': None, 'filter': [direct_token, indirect_token], 'prefix': 'as'})

# defaults when editing outside a template
outside_template = u"DefineIAction(Verb)", u"DefineTAction(Verb)", u"DefineTIAction(Verb)", u"VerbRule(Verb)", u"class"

# reserved keywords for tads language
reserved_words = ("break", "case", "catch", "class", "case", "continue", "do", "default", "delete", "else", "enum",
                  "finally", "for", "foreach", "function", "goto", "if", "intrinsic", "local", "modify", "new", "nil",
                  "property", "replace", "return", "self", "switch", "throw", "token", "true", "try", "while", "end")


class ColorSchemer:

    def __init__(self):

        # constructor for ColorSchemer, set default colors and fonts
        font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.face = font.GetFaceName()
        self.size = font.GetPointSize()
        self.colors = None

        # attempt to load default color config
        path = MessageSystem.MainWindow.get_instance().themes_path
        try:
            self.load_colors(os.path.join(path, "Obsidian.xml"))
        except Exception, e:
            print ("Could not load default theme - Obsidian.xml, using built-in default")
            tree = ET.ElementTree(ET.fromstring(embedded.obsidian))
            self.colors = tree.getroot()

    def set_color(self, color, tag, dictionary):

        # set color in dictionary according to tag
        # we have to encompass this in a try block because python stc implentations vary
        try:
            dictionary[getattr(wx.stc, color)] = tag
        except AttributeError, a:

            # silent fail on exception, log to console
            print ("wxPython 3.0 or higher required for " + color)

    def load_colors(self, filename):

        # load color settings from xml file
        try:
            tree = ET.parse(filename)
            self.colors = tree.getroot()
        except IOError, e:
            MessageSystem.error("Could not locate file: " + e.filename, "Theme Change Unsuccessful")
            tree = ET.ElementTree(ET.fromstring(embedded.obsidian))
            self.colors = tree.getroot()

    def update_colors(self, ctrl):

        # set styles from xml colors tree in memory
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
        foregrounds = {}
        [self.set_color(c, t, foregrounds) for c, t in text_styles]
        for key, value in foregrounds.iteritems():
            for c in self.colors:
                weight = ''
                if key == wx.stc.STC_T3_BLOCK_COMMENT or key == wx.stc.STC_T3_LINE_COMMENT:
                    weight = ',italic'
                if key == wx.stc.STC_T3_KEYWORD:
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

        # check brace matching
        self.Bind(wx.stc.EVT_STC_UPDATEUI, self.update_ui)

        # autoindent system
        self.Bind(wx.stc.EVT_STC_CHARADDED, self.on_char_added)

        # set lexer to tads 3
        self.SetLexer(wx.stc.STC_LEX_TADS3)
        self.SetKeyWords(0, ' '.join(reserved_words))

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

        # current template
        self.template = None

    def on_char_added(self, event):

        # don't add if we're in string or comment
        anchor_at_style = self.GetStyleAt(self.GetAnchor())
        if check_for_plain_style(anchor_at_style) is False:
            return

        # when return key char is added, handle autoindent
        if event.GetKey() == 10:

            # check if we've just added an object or class
            line = self.GetCurrentLine()
            if line > 0:
                search_line = self.Text.split('\n')[line - 1]
                if search_line:
                    if search_line[0] == '+' or ':' in search_line and search_line[0].isalpha():
                        self.AddText("\n;\n")
                        self.SetLineIndentation(line, self.GetLineIndentation(line) + (self.GetIndent() * 1))
                        self.SetAnchor(self.GetAnchor() - 3)
                        self.SetCurrentPos(self.GetCurrentPos() - 3)
                        return

            # otherwise, standard auto-indent
            self.auto_indent()

        # when bracket is added, autoadd matching close bracket
        if event.GetKey() == 123:
            self.AutoCompCancel()
            self.SetAnchor(self.GetAnchor() - 1)
            self.SetCurrentPos(self.GetCurrentPos())
            self.ReplaceSelection(u"\n{\n\n}")
            line = self.GetCurrentLine()
            indent = self.GetLineIndentation(line + 1)
            self.SetLineIndentation(line - 2, indent + (self.GetIndent() * 1))
            self.SetLineIndentation(line - 1, indent + (self.GetIndent() * 2))
            self.SetLineIndentation(line, indent + (self.GetIndent() * 1))
            self.SetAnchor(self.GetAnchor() - (indent + self.GetIndent() + 2))
            self.SetCurrentPos(self.GetCurrentPos() - (indent + self.GetIndent() + 2))

        # when quotes added, autoadd quotes
        if event.GetKey() == 34:
            self.replace_with_enclosure(u"\" \"")
        if event.GetKey() == 39:
            self.replace_with_enclosure(u"\'\'")

        # handle autocompletion too
        self.auto_complete()

    def replace_with_enclosure(self, enclosure):

        # replace current word we're editing with an enclosure of some kind, from string passed above
        # used specifically for autocomp system
        self.AutoCompCancel()
        self.WordLeftExtend()
        self.ReplaceSelection(enclosure)
        self.SetAnchor(self.GetAnchor() - 2)
        self.SetCurrentPos(self.GetCurrentPos() - 2)

    def auto_code_selected(self, event):

        # we've selected an auto completion expression! under certain conditions,
        # we may choose to code templates
        selection = event.GetText()

        # for when we insert anything ending in the word "Desc" add double quotes
        if selection[-4:] == u"Desc":
            self.replace_with_enclosure(selection + u" = \" \"")

        # for when we insert anything ending in the word "Msg" add single quotes
        if selection[-3:] == u"Msg":
            self.replace_with_enclosure(selection + u" = ' '")

        # regions
        if selection == u"regions":
            self.replace_with_enclosure(selection + u" = [  ]")

        # for define indirect action
        if u"DefineIAction" in selection:
            self.InsertText(self.GetCurrentPos(), self.insert_indent(1) + u"execAction(cmd)" + self.insert_indent(1) +
                            u"{" + self.insert_indent(2) + u"\"{You} can't do that now. \";" +
                            self.insert_indent(1) + u"}" + self.insert_indent(0) + ";")

        # for T action
        if u"DefineTAction" in selection:
            self.InsertText(self.GetCurrentPos(), self.insert_indent(0) + ";")

        # for TI action
        if u"DefineTIAction" in selection:
            self.InsertText(self.GetCurrentPos(), self.insert_indent(0) + ";")

        # for new verb rules
        if u"VerbRule" in selection:
            self.InsertText(self.GetCurrentPos(), self.insert_indent(1) + u"'verb'"
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
            if obj in self.notebook.objects:
                return [m.name for m in self.notebook.objects[obj].members]

    def find_object_template(self):

        # determine if caret is presently editing an object template
        # first clip out a few lines nearest the ; and the cursor
        end = self.Text.rfind('\n', 0, self.GetCurrentPos())
        start = self.Text.rfind('\n;\n', 0, end)
        if start < 0:
            start = 1
        if end >= len(self.Text):
            end = len(self.Text) - 1
        line = (l.strip('+ ') for l in reversed(self.Text[start:end].split('\n')) if l if l[0] != ' ').next()

        # we've got our lines, search for object template
        if line == ';':

            # we're not in a template
            self.template = None
            return

        # object template definition found here by looking for :
        if ':' in line:
            obj = line[:line.find(":")]

            # we are presently in an object template, get data on it
            if obj in self.notebook.objects:
                self.template = self.notebook.objects[obj]

            else:

                # not already in object cache, find inherited classes
                classes = re.search(": ([\w|,|\s]*)", line)
                if classes:
                    self.template = TadsParser.TClass()
                    self.template.inherits = [i.strip() for i in classes.group(1).split(u',')]
                    self.template.members = TadsParser.get_members(self.template.inherits, self.notebook.classes, self.notebook.modifys)
                    return

        # otherwise, look for pluses
        if len(line) > 2:
            if line[0] == '+' or line[1] == '+':

                classes = re.search("\+\s([\w|,|\s]*)", line)
                if classes:
                    self.template = TadsParser.TClass()
                    self.template.inherits = [i.strip() for i in classes.group(1).split(u',')]
                    self.template.members = TadsParser.get_members(self.template.inherits, self.notebook.classes, self.notebook.modifys)
                    return

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

        # update object template
        self.find_object_template()

        # analyze code based on present template and line in context
        for enclosure, suggestions, flags in analyzer:
            if enclosure in context:
                if suggestions:
                    results.extend(suggestions)
                if 'classes' in flags:
                    results = self.notebook.classes
                if 'members' in flags:
                    members = self.find_object_methods(full_line[:caret])
                    if members:
                        results = members
                if 'objects' in flags:
                    results.extend(self.notebook.objects)
                    results.extend(self.notebook.global_tokens)
                if 'self' in flags:
                    if self.template:
                        results.extend(m.name for m in self.template.members)
                if 'filter' in flags:
                    results = [r for f in flags['filter'] for r in results if f in r]
                if 'prefix' in flags:
                    results = [flags['prefix'] + r.title() for r in results]

        # still no results, figure out if we're in a object template
        if not results:
            if self.template:
                results.extend([m.name for m in self.template.members])
                results.extend(self.notebook.objects)
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

    def context_help(self):

        # display context help from valid word in call tip box
        # start by getting the full word the caret is on top of
        search_string = self.get_full_word()
        if search_string in self.notebook.classes:
            return self.notebook.classes[search_string].help

        # search for help in classes matching the search string
        member = prep_member(search_string)

        # we may be looking at a global
        if u'(' in search_string:
            global_token = (g.help for g in self.notebook.global_tokens.values() if u'(' in g.name
                            if search_string[:search_string.find(u'(')] == g.name[:g.name.find(u'(')]).next()
            if global_token:
                return global_token
        else:
            global_token = (g.help for g in self.notebook.global_tokens.values() if search_string == g.name).next()
            if global_token:
                return global_token

        # search current line for help data
        full_line, caret = self.GetCurLine()
        if '.' in full_line[:caret]:
            tokens = re.split('[{0}]'.format(re.escape(" [](){};")), full_line[:caret])
            the_object = tokens[-1].split(".")[0]
            if the_object:
                if the_object in self.notebook.objects:
                    return next(m.help for m in self.notebook.objects[the_object].members if member == prep_member(m.name))

        # search by current object template
        self.find_object_template()
        if self.template:
            return next((m.name + ": " + m.help) for m in self.template.members if search_string == prep_member(m.name) if m.help != "")

    def update_ui(self, event):

        # check brace highlighting
        self.check_brace()

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
            with codecs.open(path + "/" + filename, 'w', "utf-8") as f:
                f.write(self.Text)
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
        errors = atd.checkDocument(strings, "TadsPad_" + self.GetTopLevelParent().project.name)

        # pull in ignored words from ignored.txt
        ignored_file = open(os.path.join(project.path, "ignore.txt"), 'rU')
        ignored_words = ignored_file.read().split("\n")
        ignored_file.close()
        for error in errors[:]:
            if error.string in ignored_words:
                errors.remove(error)

        # we now have a list of spelling errors, display to user
        if errors:
            speller = SpellCheckerWindow.SpellCheckWindow(wx.GetTopLevelWindows(), errors, self, project)
            speller.ShowModal()
        MessageSystem.info("No spelling errors found in this file.", "Hurray!")

    def check_brace(self):

        # cut if position is too high or too low
        i = self.GetCurrentPos()
        if i == 0 or i > len(self.Text) - 1:
            return

        # check for brace match in current window - but watch out for quotes or comments
        style = self.GetStyleAt(i)
        if check_for_plain_style(style):

            # we're not in a quote, do we have a brace?
            character = self.Text[i]
            if '{' in character:
                match = self.BraceMatch(i)
                if match != -1:
                    self.BraceHighlight(i, match)
                    return
                else:
                    self.BraceBadLight(i)
                    return

        self.BraceBadLight(-1)


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
    # as a temp debugging measure, we have removed paranths from separator test

    if char.isspace():
        return True
    separators = '.', '[', ']', '{', '}'
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

            # this fixes a weird bug with the asDobjFor macros
            return_value.append(word.replace("asDobjfor", "asDobjFor"))
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
            break
        return_value += c
    return return_value

def search(code, line):

    # scan current code for possible enclosures we're in
    # look first in current line, then in all code
    # the order here is important, by the way
    if len(line) > 2:
        if line[0] == '+' or line[1] == '+':
            return ':'
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
