

# class for preferences editor window

import wx


class PrefsEditWindow(wx.Dialog):

    def __init__(self, prefs):
        wx.Dialog.__init__(self, None, title="Edit Preferences", style=wx.CHOICEDLG_STYLE | wx.TAB_TRAVERSAL)

        # init new prefs dialog
        self.prefs = prefs
        screen_geometry = wx.Display().GetGeometry()
        width = screen_geometry.Width / 2
        height = screen_geometry.Height / 2
        self.SetSize(wx.Size(width, height))
        contents = wx.BoxSizer(wx.VERTICAL)
        self.tadsText = wx.TextCtrl(parent=self)
        self.tadsButton = wx.Button(parent=self)
        self.tadsButton.SetLabel("Find TADS3 Path")
        self.terpText = wx.TextCtrl(parent=self)
        self.terpButton = wx.Button(parent=self)
        self.terpButton.SetLabel("Find Interpreter")
        contents.Add(wx.StaticText(parent=self, label="TADS 3 Folder:"), 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.tadsText, 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.tadsButton, 0, wx.ALL, border=width / 50)
        contents.Add(wx.StaticLine(parent=self), 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(wx.StaticText(parent=self, label="Interpreter Folder:"), 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.terpText, 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.terpButton, 0, wx.ALL, border=width / 50)
        self.SetSizer(contents)

        # set default values to prefs passed in function argument
        self.tadsText.SetValue(self.prefs["tadspath"])
        self.terpText.SetValue(self.prefs["terp"])
        self.Layout()
        self.Update()

__author__ = 'dj'
