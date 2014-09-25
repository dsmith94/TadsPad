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
import CodeCompletion
import xml.etree.ElementTree as ET

# english defaults for verify, check , etc...
verify_token = u"verify"
check_token = u"check"
action_token = u"action"
direct_token = u"dobjFor"
indirect_token = u"iobjFor"
accessory_token = u"aobjFor"
remap_direct_token = u"asDobjFor"
remap_indirect_token = u"asIobjFor"
remap_accessory_token = u"asAobjFor"
inObj_suggestions = (u"preCond", verify_token + u"()", check_token + u"()", action_token + u"()")
verify_suggestions = (u"logicalRank(rank, key);", u"dangerous", u"illogicalNow(msg, params);", u"illogical(msg, params);",
                      u"illogicalSelf(msg, params);", u"nonObvious", u"inaccessible(msg, params);")
q_suggestions = (u"scopeList(actor)", u"topicScopeList()", u"inLight(a)", u"canSee(a, b)", u"canHear(a, b)",
                 u"canSmell(a, b)", u"canReach(a, b)", u"sightBlocker(a, b)", u"reachBlocker(a, b)",
                 u"soundBlocker(a, b)", u"scentBlocker(a, b)")


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

# defaults when editing outside a template
outside_template = (u"DefineIAction(Verb)", u"DefineTAction(Verb)", u"DefineTIAction(Verb)", u"VerbRule(Verb)", u"class", u"modify")

# reserved keywords for tads language
reserved_words = ("break", "case", "catch", "class", "case", "continue", "do", "default", "delete", "else", "enum",
                  "finally", "for", "foreach", "function", "goto", "if", "intrinsic", "local", "modify", "new", "nil",
                  "property", "replace", "return", "self", "switch", "throw", "token", "true", "try", "while", "end")

# suggestables - always suggest these in an enclosure
enclosure_suggestions = ("break", "case", "catch", "case", "continue", "do", "default", "delete", "else", "enum",
                        "finally", "for", "foreach", "function", "goto", "if", "intrinsic", "local", "new", "nil",
                        "property", "replace", "return", "self", "switch", "throw", "token", "true", "try", "while",
                        "end")


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

        # track whether we're in standard coding
        self.in_standard_code = False

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

    def no_semicolon(self):

        """
        Look for a lack of semicolon, usually after we've just added a class or object
        """

        # look for semicolon or alphanumeric
        position = self.GetCurrentPos()
        for c in self.Text[position:-1]:
            if c == u';':

                # we have semicolon, return false
                return False

            if not c.isspace():

                # return otherwise if non-white char is found
                return True
        return True

    def on_char_added(self, event):

        key = event.GetKey()

        # certain keycodes will cancel autocomp, like spaces or brackets
        cancel_codes = (32, 123, 125, 91, 93, 40, 41, 61, 43, 46, 47, 92, 45, 42, 39, 38, 37, 36, 35)

        # get context
        full_line, caret = self.GetCurLine()

        # don't add if we're in string or comment
        anchor_at_style = self.GetStyleAt(self.GetAnchor())
        if check_for_plain_style(anchor_at_style) is False:
            return

        # when return key char is added, handle autoindent
        if key == 10:

            # check if we've just added an object or class
            line = self.GetCurrentLine()
            if line > 0:
                search_line = self.GetLineUTF8(line - 1)
                if search_line:
                    if search_line[0] == u'+' or u':' in search_line and search_line[0].isalpha():
                        if self.no_semicolon():
                            self.AddText(u"\n;\n")
                            self.SetLineIndentation(line, self.GetLineIndentation(line) + (self.GetIndent() * 1))
                            self.SetAnchor(self.GetAnchor() - 3)
                            self.SetCurrentPos(self.GetCurrentPos() - 3)
                        return

            # otherwise, standard auto-indent
            self.auto_indent()

        # when bracket is added, autoadd matching close bracket
        if key == 123:
            addNewLine = u""
            if full_line.strip() != u"{":
                addNewLine = u"\n"
            self.AutoCompCancel()
            indent = self.GetLineIndentation(self.GetCurrentLine())
            self.SetAnchor(self.GetAnchor() - 1)
            self.SetCurrentPos(self.GetCurrentPos())
            self.ReplaceSelection(addNewLine + u"{\n\n}")
            line = self.GetCurrentLine()
            self.SetLineIndentation(line - 2, indent)
            self.SetLineIndentation(line - 1, indent + (self.GetIndent()))
            self.SetLineIndentation(line, indent)
            new_position = self.PositionFromLine(line) - 1
            self.SetAnchor(new_position)
            self.SetCurrentPos(new_position)

        # handle autocompletion too
        if key not in cancel_codes:
            self.auto_complete()
        else:
            self.AutoCompCancel()

        # when quotes added, autoadd quotes
        if key == 34:

            # handle autoadd quotes differently when in standard coding
            if self.in_standard_code:
                self.replace_with_enclosure(u"\" \";")
                self.SetAnchor(self.GetAnchor() - 1)
                self.SetCurrentPos(self.GetCurrentPos() - 1)
            else:
                self.replace_with_enclosure(u"\" \"")

        #if event.GetKey() == 39:
        #    self.replace_with_enclosure(u" \'\'")

    def replace_with_enclosure(self, enclosure):

        # replace current word we're editing with an enclosure of some kind, from string passed above
        # used specifically for autocomp system
        self.AutoCompCancel()
        self.WordLeftExtend()
        self.ReplaceSelection(enclosure)
        self.SetAnchor(self.GetAnchor() - 2)
        self.SetCurrentPos(self.GetCurrentPos() - 2)

    def auto_code_selected(self, event):

        # only complete if we're all thats on a line
        full_line, caret = self.GetCurLine()
        if caret < len(full_line) - 1:
            return

        # we've selected an auto completion expression! under certain conditions,
        # we may choose to code templates
        selection = event.GetText()

        # insert any of the inObj suggestions, add brackets
        if selection in inObj_suggestions:
            indent = self.GetLineIndentation(self.GetCurrentLine())
            self.AutoCompCancel()
            self.WordLeftExtend()
            self.ReplaceSelection(selection + u'\n{\n\n}')
            line = self.GetCurrentLine()
            self.SetAnchor(self.GetAnchor() - 1)
            self.SetCurrentPos(self.GetCurrentPos() - 1)
            self.SetLineIndentation(line - 2, indent)
            self.SetLineIndentation(line - 1, indent + (self.GetIndent()))
            self.SetAnchor(self.GetAnchor() - 1)
            self.SetCurrentPos(self.GetCurrentPos() - 1)
            self.SetLineIndentation(line, indent)

        # for when we insert anything ending in the word "Desc" add double quotes
        if selection[-4:] == u"Desc":
            self.replace_with_enclosure(selection + u" = \" \"")

        # for when we insert anything ending in the word "Msg" add single quotes
        if selection[-3:] == u"Msg":
            self.replace_with_enclosure(selection + u" = ' '")

        # regions
        if selection == u"regions":
            self.replace_with_enclosure(selection + u" = [  ]")

        # inherited
        if selection[:9] == u"inherited":
            if self.in_standard_code:
                self.AutoCompCancel()
                self.WordLeftExtend()
                self.ReplaceSelection(selection + u';')

        # for define indirect action
        if u"DefineIAction" in selection:
            self.InsertText(self.GetCurrentPos(), self.insert_indent(1) + u"execAction(cmd)" + self.insert_indent(1) +
                            u"{" + self.insert_indent(2) + u"\"{You} can't do that now. \";" +
                            self.insert_indent(1) + u"}" + self.insert_indent(0) + ";")

        # for T action
        if u"DefineTAction" in selection:
            self.InsertText(self.GetCurrentPos(), self.insert_indent(0) + u";")

        # for TI action
        if u"DefineTIAction" in selection:
            self.InsertText(self.GetCurrentPos(), self.insert_indent(0) + u";")

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

        """
        find object on a single line
        return methods
        """

        # first get everything after character delineators
        token = u""
        delins = u" [](){};"
        for c in reversed(line):
            if c in delins:
                break
            else:
                token = c + token

        # if we have an object to edit, find it in the notebook object database (by name)
        obj = token[:token.find(u".")]
        if obj:
            if obj in self.notebook.objects:
                members = []

                # remove following line if usefulness is not demonstrated soon
                members.extend([m.name for m in self.notebook.objects[obj].keywords])
                members.extend([m.name for i in self.notebook.objects[obj].inherits if i in self.notebook.classes for m in TadsParser.get_members(self.notebook.classes[i].inherits, self.notebook.classes, self.notebook.modifys)])
                return members
            else:

                # special rules for Q object
                if obj == u'Q':
                    return q_suggestions
                else:
                    return 'no object'
        return None

    def find_object_template(self, code):

        # determine if caret is presently editing an object template
        # first clip out a few lines nearest the ; and the cursor
        end = code.rfind('\n', 0, self.GetCurrentPos())
        start = code.rfind('\n;\n', 0, end)
        if start < 0:
            start = 1
        if end >= len(code):
            end = len(code) - 1
        try:
            line = (l.strip(u'+ ') for l in reversed(code[start:end].split('\n')) if l if l[0] != u' ').next()
        except StopIteration:
            line = u""

        # we might have a template, search for it
        inherits = TadsParser.get_inherits(line)
        if inherits:
            self.template = TadsParser.TClass()
            self.template.inherits = inherits
            self.template.members = TadsParser.get_members(self.template.inherits, self.notebook.classes, self.notebook.modifys)

    def auto_complete(self):

        # engine to analyze code suggest keywords
        # conducted in a series of stages

        # stage 1: get context of caret for code completion
        full_line, caret = self.GetCurLine()
        start = self.Text[:self.GetCurrentPos()].rfind(u'\n;\n')
        if start < 0:
            start = 0
        cleaned = clean_string(self.Text[start:self.GetCurrentPos()])
        context = CodeCompletion.context(caret, full_line, cleaned)

        # stage 2: take the processed code and find
        # the classes of the object we're editing, plus the present enclosures
        # and only continue if some suggestions are present
        suggestions = self.build_suggestions(context, cleaned)
        if not suggestions:
            self.AutoCompCancel()
            return

        # stage 3: finally, gather context data from entered word
        # make string to send to the stc autocompletion box
        # note - separator betwixt keywords in final string is a ^
        present_word = self.get_word()
        if len(present_word) < 1:
            return
        if "=" in present_word:
            return
        if len(suggestions) > 0:
            self.AutoCompShow(len(present_word), suggestions)
        else:
            self.AutoCompCancel()

    def build_suggestions(self, context, code):

        """
        build suggestions from the context and code passed above
        """

        # this is unfortunately quite complex, because of the nature of code completion
        results = []
        full_line, caret = self.GetCurLine()
        line = full_line[:caret]

        # by default, we are not in standard coding
        self.in_standard_code = False

        # update object template
        self.find_object_template(code)

        # analyze code based on present template and line in context
        if 'classes' in context:
            results.extend(self.notebook.classes)
        if 'properties' in context:
            members = self.find_object_methods(line)
            if members:
                if members == 'no object':
                    # no object on other end of period - return blank
                    return
                context.add('no template suggestions')
                results = members
        if 'verify' in context:
            results.extend(verify_suggestions)
        if 'objects' in context:
            results.extend(self.notebook.objects)
            results.extend(self.notebook.global_tokens)
        if 'actions' in context:
            results = self.notebook.actions
            context.add('no template suggestions')
        for token in (direct_token, indirect_token, accessory_token):
            if token in context:
                if verify_token not in code and check_token not in code and action_token not in code:
                    results = [i for i in inObj_suggestions]
                    context.add('no template suggestions')
                    context.add('properties')
                    break
        for remap in (remap_direct_token, remap_indirect_token, remap_accessory_token):
            if remap in context:
                results = [remap + u"(" + x + u")" for x in self.notebook.actions]
                context.add('no template suggestions')
                break

        # next figure out if we're in a object template
        # if not results:
        if 'no template suggestions' not in context:
            if self.template:
                results.extend([m.name for m in self.template.members if hasattr(m, 'name')])
                results.extend(self.template.keywords)
            else:
                results = [i for i in outside_template]

        # add reserved tads words if we are in a bracketed enclosure
        # remove the objFor suggestions
        # only do this next bit of code if "properties" is not a context requirement
        if "properties" not in context:
            if u"{" in code:
                results = self.get_standard_coding_suggestions(results)
                inherited = get_inherited(code)
                if inherited is not None:
                    results.append(u'inherited(' + inherited + u')')
                else:
                    results.append(u'inherited')

                # flag they we're in standard code
                self.in_standard_code = True

            else:

                # same deal if we're in << enclosure in quotes
                if u"<<" in line and u">>" not in line:
                    results = self.get_standard_coding_suggestions(results)

        # finalize for return
        results = list(set(results))
        results = filter_suggestions(self.get_word(), results)
        results.sort()
        return '^'.join(results)

    def get_standard_coding_suggestions(self, results):

        """
        Take the list passed above and extend it so we're ready for standard coding
        """

        suggestions = (enclosure_suggestions, self.notebook.objects, self.notebook.classes)
        [results.extend(s) for s in suggestions]

        # always remove objFor stuff for standard coding
        results = [entry for entry in results if u"objFor" not in entry]
        return results

    def get_word(self):

        # return string of recently typed chars at the caret position
        anchor_position = self.GetAnchor() - 1
        if anchor_position >= len(self.Text):
            return ""
        for char_index in xrange(anchor_position, 1, -1):
            char = self.Text[char_index]
            if word_boundary(char) or char == u'(':
                return self.Text[char_index + 1:anchor_position + 1].strip(u".").strip(u"@").strip()
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
        global_token = find_global_token(search_string, self.notebook.global_tokens.values())
        if global_token:
            return global_token

        # search current line for help data
        full_line, caret = self.GetCurLine()
        if '.' in full_line[:caret]:
            tokens = re.split('[{0}]'.format(re.escape(" [](){};")), full_line[:caret])
            the_object = tokens[-1].split(".")[0]
            if the_object:
                if the_object in self.notebook.objects:
                    for m in self.notebook.objects[the_object].members:
                        if member == prep_member(m.name):
                            return m.help

        # search by current object template
        self.find_object_template(clean_string(self.Text[0:self.GetAnchor() - 1]))
        if self.template:
            for m in self.template.members:
                if search_string == prep_member(m.name):
                    if m.help:
                        return m.name + ": " + m.help

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

    def search_for(self, text, in_strings=False, case_sensitive=True):

        # select text from anchor
        if in_strings:
            search_in_text = TadsParser.extract_strings(self.Text)
        else:
            search_in_text = self.Text
        if not case_sensitive:
            text = text.lower()
            search_in_text = search_in_text.lower()
        maxPos = len(search_in_text)
        textLength = len(text)
        minPos = self.GetAnchor() + 1
        location = search_in_text.find(text, minPos, maxPos)
        if location != -1:
            self.GotoPos(location)
            self.SetAnchor(location)
            self.SetCurrentPos(location + textLength)

    def replace_with(self, old, new, minPos, in_strings=False, case_sensitive=True):

        # replace one string within selection
        if in_strings:
            search_in_text = TadsParser.extract_strings(self.Text)
        else:
            search_in_text = self.Text
        maxPos = len(search_in_text)
        textLength = len(new)
        if minPos == -1:
            minPos = self.GetAnchor()
        if not case_sensitive:
            old = old.lower()
            search_in_text = search_in_text.lower()
        location = search_in_text.find(old, minPos, maxPos)
        if location != -1:
            text = self.Text[location:]
            self.BeginUndoAction()
            text = text.replace(old, new, 1)
            self.EndUndoAction()
            self.Text = self.Text[:location] + text
            self.GotoPos(location)
            self.SetAnchor(location)
            self.SetCurrentPos(location + textLength)

    def replace_all_with(self, old, new, in_strings, case_sensitive=True):

        # replace all instances in editor of old with new string
        if in_strings:
            search_in_text = TadsParser.extract_strings(self.Text)
        else:
            search_in_text = self.Text
        if not case_sensitive:
            old = old.lower()
            search_in_text = search_in_text.lower()
        lst = [i for i, char in enumerate(search_in_text) if search_in_text[i:len(old) + i] == old]
        replaced = TadsParser.replace_next(self.Text, lst, old, new)
        if replaced:
            self.BeginUndoAction()
            self.Text = replaced
            self.EndUndoAction()

    def spellcheck(self, project):

        # pull strings from page and send to atd spellcheck service
        strings = TadsParser.extract_strings(self.Text)

        # remove escapes from contractions
        strings = strings.replace(u"\\'", u"\'")

        # send to atd
        errors = atd.checkDocument(strings, "TadsPad_" + self.GetTopLevelParent().project.name)

        # pull in ignored words from ignored.txt
        ignored_file = open(os.path.join(project.path, "ignore.txt"), 'rU')
        ignored_words = ignored_file.read().split("\n")
        ignored_file.close()
        for error in errors[:]:
            if error.string in ignored_words:
                errors.remove(error)

        # only allow spelling errors
        errors = [e for e in errors if e.description == "Spelling"]

        # and remove duplicates
        #clean_list = []
        #for e in errors:
        #    if e.string not in [l.string for l in clean_list]:
        #        clean_list.append(e)
        #errors = clean_list

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


def find_global_token(search_string, tokens):

    """
    Get global token from text, return None otherwise if not exists
    """

    # find global token in text
    if u'(' in search_string:
        for g in tokens:
            if u'(' in g.name:
                if search_string[:search_string.find(u'(')] == g.name[:g.name.find(u'(')]:
                    return g.help
    else:
        for g in tokens:
            if search_string == g.name:
                return g.help
    return None


def clean_string(code):

    """
    return a string of code with strings, quotes and bracketed code removed
    """

    code = TadsParser.clean(code, False)

    # remove brackets and action remaps too
    process = (consolidate_brackets, remove_bracketed_enclosures, remove_remaps)
    for cleaning in process:
        code = cleaning(code)

    return code


def remove_remaps(code):

    """
    Return a string of code containing no action-remaps so we don't confuse code analysis engine
    """

    code = code.split(u"\n")
    tokens = (remap_direct_token, remap_indirect_token, remap_accessory_token)
    for index, line in enumerate(code[:]):
        for token in tokens:
            if token in line:
                code[index] = line.replace(u'objFor', u'xxxxxx')
    return u'\n'.join(code)


def consolidate_brackets(code):

    """
    consolidate brackets to same line as function or member for processing
    return code as string
    """

    in_bracket = False
    result = []
    for index, c in reversed(list(enumerate(code))):
        if c == u"{":

            # we're in a bracket, now remove all spaces and tabs
            in_bracket = True

        # add to final returned result if not in bracket or if not whitespace
        if not in_bracket:
            result.append(c)
        else:
            if c != u"\t" and c != u" " and c != u"\n":
                result.append(c)

        if c == u"\n":

            # no longer in bracket search
            in_bracket = False

    return u"".join(reversed(result))


def clean_string_old(code):

    # return a string of code with strings, quotes, and bracketed code removed
    # note that this is a specialty cleaning function, and CANNOT be replace by TadsParser.clean, which is
    # somewhat similiar

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
    removed_strings = pattern_enclosure.sub("{", removed_strings)
    removed_strings = remove_bracketed_enclosures(removed_strings)

    return removed_strings


def get_inherited(code):

    """
    Retrieve inherited parameters, return if they exist, skip objFors
    """

    # cut out objFors
    clip_to = 0
    for token in (direct_token, indirect_token, accessory_token):
        if token in code:
            clip_to = code.find(u'\n', code.find(token))
    code = code[clip_to:]

    # now, continue with our regularly shceduled algorithm
    end = code.find(u'){')
    start = code.find(u'(')
    if start > -1:
        if end > start:
                parameters = code[start + 1:end]
                if parameters != u"":
                    return parameters
    return None


__author__ = 'dj'
