

import wx

# display messages to user from this control


class MessagePane(wx.Panel):

    def __init__(self, parent):

        ## new instance of message pane
        wx.Panel.__init__(self, parent=parent)
        r = wx.Display().GetGeometry()
        self.text_control = wx.TextCtrl(self, -1, "", wx.DefaultPosition, (r.Width, r.Height / 5), wx.NO_BORDER | wx.TE_MULTILINE)
        self.debug_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.debug_list.SetSize((r.Width, r.Height / 5))
        self.debug_list.InsertColumn(0, "Output", width=r.Width)

    def show_message(self, text):

        # display a text message for user
        self.debug_list.Hide()
        self.text_control.Show()
        self.text_control.Clear()
        self.text_control.AppendText(text)

    def show_output(self, list):

        # display output onscreen
        self.text_control.Hide()
        self.debug_list.Show()

__author__ = 'dj'
