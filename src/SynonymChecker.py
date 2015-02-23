

#
#   Synonym Checker Window, to provide user with list of nouns and verbs
#

import wx
import os
import codecs
import TadsParser
import MessageSystem


class CheckWindow(wx.Frame):
    def __init__(self, word, nouns, verbs, editor):
        wx.Frame.__init__(self, None)

        # set up synonym check analyze window
        self.Title = "Find synonyms for: " + word
        r = wx.Display().GetGeometry()
        self.editor = editor
        self.word = word
        self.nouns_ctrl = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.nouns_ctrl.InsertColumn(0, "Nouns", width=r.Width / 2)
        self.nouns_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.word_activated)
        self.verbs_ctrl = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.verbs_ctrl.InsertColumn(0, "Verbs", width=r.Width / 2)
        self.verbs_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.word_activated)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.nouns_ctrl, 5, wx.EXPAND | wx.ALL)
        sizer.Add(self.verbs_ctrl, 5, wx.EXPAND | wx.ALL)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
        self.Fit()
        self.Maximize()
        for suggestion in nouns:
                self.nouns_ctrl.InsertStringItem(0, suggestion)
        for suggestion in verbs:
                self.verbs_ctrl.InsertStringItem(0, suggestion)

    def word_activated(self, event):

        # change noun under editor selection
        text = str(event.GetItem().GetText())
        if self.editor.GetSelectedText() == self.word:
            self.editor.ReplaceSelection(text)
        self.Close()


__author__ = 'dj'
