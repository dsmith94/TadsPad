

# class for preferences editor window

import wx


class PrefsEditWindow(wx.Dialog):

    def __init__(self, prefs):
        wx.Dialog.__init__(self, None, title="Edit TADS Path Location", style=wx.CHOICEDLG_STYLE | wx.TAB_TRAVERSAL)

        # init new prefs dialog
        self.prefs = prefs
        screen_geometry = wx.Display().GetGeometry()
        width = screen_geometry.Width / 2
        height = screen_geometry.Height / 2
        self.SetSize(wx.Size(width, height))
        contents = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.tadsText = wx.TextCtrl(parent=self)
        self.tadsButton = wx.Button(parent=self, label="Find T3 Compiler")
        self.tadsButton.Bind(wx.EVT_BUTTON, self.find_tads)
        self.terpText = wx.TextCtrl(parent=self)
        self.terpButton = wx.Button(parent=self, label="Find Interpreter")
        self.terpButton.Bind(wx.EVT_BUTTON, self.find_terp)
        self.terminalText = wx.TextCtrl(parent=self)
        self.okButton = wx.Button(parent=self, label='Ok')
        self.okButton.Bind(wx.EVT_BUTTON, self.finalize)
        self.cancelButton = wx.Button(parent=self, label='Cancel')
        self.cancelButton.Bind(wx.EVT_BUTTON, self.custom_close_button)
        contents.Add(wx.StaticText(parent=self, label="TADS 3 Folder:"), 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.tadsText, 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.tadsButton, 0, wx.ALL, border=width / 50)
        contents.Add(wx.StaticLine(parent=self), 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(wx.StaticText(parent=self, label="Interpreter Folder:"), 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.terpText, 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.terpButton, 0, wx.ALL, border=width / 50)
        contents.Add(wx.StaticLine(parent=self), 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(wx.StaticText(parent=self, label="Terminal Emulator (unused on Windows platforms):"),
                     0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(self.terminalText, 0, wx.ALL, border=width / 50)
        buttons.Add(self.okButton, 0, wx.ALL, border=width / 50)
        buttons.Add(self.cancelButton, 0, wx.ALL, border=width / 50)
        contents.Add(wx.StaticLine(parent=self), 0, wx.EXPAND | wx.ALL, border=width / 50)
        contents.Add(buttons, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
        self.SetSizer(contents)

        # set default values to prefs passed in function argument
        self.tadsText.SetValue(self.prefs["tadspath"])
        self.terpText.SetValue(self.prefs["terp"])
        self.terminalText.SetValue(self.prefs["terminal"])
        self.Layout()
        self.Fit()
        self.Update()

    def finalize(self, event):

        # change prefs according to what we've set here on this window
        self.prefs["tadspath"] = self.tadsText.GetValue().replace("\\", "/")
        self.prefs["terp"] = self.terpText.GetValue().replace("\\", "/")
        self.prefs["terminal"] = self.terminalText.GetValue().replace("\\", "/")
        self.Destroy()

    def custom_close_button(self, event):

        # close window on this button press
        self.Destroy()

    def find_tads(self, event):

        # find tads compiler executable
        fd = wx.FileDialog(self, "Find t3make", "", "", "", wx.FD_OPEN)
        if fd.ShowModal() == wx.ID_CANCEL:
            return
        else:
            self.tadsText.SetValue(fd.Path)

    def find_terp(self, event):

        # find interpreter executable
        fd = wx.FileDialog(self, "Find t3 interpreter", "", "", "", wx.FD_OPEN)
        if fd.ShowModal() == wx.ID_CANCEL:
            return
        else:
            self.terpText.SetValue(fd.Path)


__author__ = 'dj'
