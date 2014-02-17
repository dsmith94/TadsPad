

# class handling find/replace window

import wx


class FindReplaceWindow(wx.Frame):
    def __init__(self, project, notebook):
        wx.Frame.__init__(self, None, title="Find and Replace", style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        # open find/replace window, store project and notebook references
        self.project = project
        self.notebook = notebook
        r = wx.Display().GetGeometry()
        self.SetSize(wx.Size(r.Width / 2, r.Height / 3))
        findLbl = wx.StaticText(parent=self, label="Find Text:")
        self.FindText = wx.TextCtrl(parent=self)
        replaceLbl = wx.StaticText(parent=self, label="Replace with:")
        self.ReplaceText = wx.TextCtrl(parent=self)
        self.FindButton = wx.Button(parent=self)
        self.FindButton.SetHelpText("Find Text String")
        self.FindButton.SetLabel("Find")
        self.FindButton.Bind(wx.EVT_BUTTON, self.FindButtonPress)
        self.ReplaceButton = wx.Button(parent=self)
        self.ReplaceButton.SetHelpText("Replace String Nearest Cursor")
        self.ReplaceButton.SetLabel("Replace")
        self.ReplaceButton.Bind(wx.EVT_BUTTON, self.ReplaceButtonPress)
        self.ReplaceFileButton = wx.Button(parent=self)
        self.ReplaceFileButton.SetHelpText("Replace All Strings in File")
        self.ReplaceFileButton.SetLabel("Replace All in File")
        self.ReplaceFileButton.Bind(wx.EVT_BUTTON, self.ReplaceAllButtonPress)
        self.CloseButton = wx.Button(parent=self)
        self.CloseButton.SetHelpText("Close Current Find/Replace Window")
        self.CloseButton.SetLabel("Close")
        self.CloseButton.Bind(wx.EVT_BUTTON, self.CustomCloseButtonEvent)
        self.status = self.CreateStatusBar()
        sizer = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(self.FindButton)
        buttons.Add(self.ReplaceButton)
        buttons.Add(self.ReplaceFileButton)
        buttons.Add(self.CloseButton)
        sizer.Add(findLbl, 0, wx.EXPAND | wx.ALL, border=r.Width / 100)
        sizer.Add(self.FindText, 0, wx.EXPAND | wx.ALL, border=r.Width / 100)
        sizer.Add(replaceLbl, 0, wx.EXPAND | wx.ALL, border=r.Width / 100)
        sizer.Add(self.ReplaceText, 0, wx.EXPAND | wx.ALL, border=r.Width / 100)
        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, border=r.Width / 100)
        self.SetBackgroundColour(self.FindButton.GetBackgroundColour())
        self.SetSizer(sizer)
        self.Fit()
        self.Update()

    def FindButtonPress(self, event):

        # press find button event
        self.notebook.find_string(self.FindText.GetValue(), self.status)

    def ReplaceButtonPress(self, event):

        # press replace button event
        self.notebook.replace_string(self.FindText.GetValue(), self.ReplaceText.GetValue(), self.status)

    def ReplaceAllButtonPress(self, event):

        # press replace all instances button event
        self.notebook.replace_all_string(self.FindText.GetValue(), self.ReplaceText.GetValue(), self.status)

    def CustomCloseButtonEvent(self, event):

        # press close button
        self.Destroy()


__author__ = 'dj'
