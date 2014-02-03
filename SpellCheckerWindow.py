
#
#   Spell Checker Window, to analyze the current file in the editor notebook
#

import wx
import atd
import os

class SpellCheckWindow(wx.Frame):
    def __init__(self, errors, editor, project):
        wx.Frame.__init__(self, None)

        # set up spell check analyze window
        self.title_prefix = "Spell\Grammar Check: "
        r = wx.Display().GetGeometry()
        self.SetSize(wx.Size(r.Width / 2, r.Height / 2))
        self.editor = editor
        self.errors = errors
        self.error = atd.Error
        self.project = project
        self.suggestions_ctrl = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.suggestions_ctrl.InsertColumn(0, "Suggestions List", width=r.Width / 2)
        self.suggestions_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.suggestion_activated)
        self.suggestions_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.suggestion_selected)
        lbl_replace = wx.StaticText(self, -1, "Replace all with:")
        self.txt_replace = wx.TextCtrl(self, -1, "", size=(175, -1), style=wx.SUNKEN_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        btn_replace = wx.Button(self, id=wx.ID_ANY, label="Replace")
        btn_replace.Bind(wx.EVT_BUTTON, self.btn_replace_activated)
        btn_ignore = wx.Button(self, id=wx.ID_ANY, label="Ignore")
        btn_ignore.Bind(wx.EVT_BUTTON, self.btn_ignore_activated)
        btn_ignore_list = wx.Button(self, id=wx.ID_ANY, label="Ignore and Add to Ignored List")
        btn_ignore_list.Bind(wx.EVT_BUTTON, self.btn_ignore_list_activated)
        buttons.Add(btn_replace)
        buttons.Add(btn_ignore)
        buttons.Add(btn_ignore_list)
        sizer.Add(self.suggestions_ctrl, 5, wx.EXPAND | wx.ALL)
        sizer.Add(lbl_replace)
        sizer.Add(self.txt_replace)
        sizer.Add(buttons, 1)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
        self.check_next_word()

    def check_next_word(self):

        # check the next word/phrase in list of errors
        # with no errors, close window
        print len(self.errors)
        if len(self.errors) < 1:
            self.Destroy()

        # otherwise, check for next error in list
        self.error = self.errors.pop(0)
        error_location = self.editor.Text.find(self.error.string)
        if error_location < 0:
            self.check_next_word()
        self.editor.GotoPos(error_location)
        self.editor.SetCurrentPos(error_location)
        self.editor.SetAnchor(error_location + len(self.error.string))
        self.SetTitle(self.title_prefix + self.error.string)
        self.suggestions_ctrl.DeleteAllItems()
        for suggestion in self.error.suggestions:
            self.suggestions_ctrl.InsertStringItem(0, suggestion)

    def replace(self, old_text, new_text):

        # replace old text with new text
        self.editor.Text = self.editor.Text.replace(old_text, new_text)
        self.check_next_word(self.errors)

    def suggestion_activated(self, event):

        # suggestion has been activated, replace all same phrases in editor
        text = event.GetText()
        self.replace(self.error.string, text)

    def suggestion_selected(self, event):

        # suggestion has been selected, change text in box
        text = event.GetText()
        self.txt_replace.SetValue(text)

    def btn_replace_activated(self, event):

        # "replace" button clicked, replace all words in text
        self.replace(self.error.string, self.txt_replace.GetValue())

    def btn_ignore_activated(self, event):

        # "ignore" button clicked, move to next suggestion
        self.check_next_word()

    def btn_ignore_list_activated(self, event):

        # ignore error, and add this error string to ignored word list
        self.ignore_word(self.error.string)
        for error in self.errors:
            if error.string is self.error.string:
                self.errors.remove(error)
        self.check_next_word()

    def ignore_word(self, new_word):

        # add word passed above to ignored words
        ignore_file = open(os.path.join(self.project.path, "ignore.txt"), 'rU')
        ignore_words = ignore_file.read()
        ignore_file.close()
        parsed_words = ignore_words.split("\n")

        # word already in file, abort
        if new_word in parsed_words:
            return

        # create new string structure to save to ignore.txt
        parsed_words.append(new_word)
        new_list = ""
        for word in parsed_words:
            if word != "":
                new_list += word + '\n'
        ignore_file = open(os.path.join(self.project.path, "ignore.txt"), 'w')
        ignore_file.write(new_list)
        ignore_file.close()


__author__ = 'dj'
