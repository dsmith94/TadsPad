# display messages to user from this control

import wx
import ErrorListCtrl


class OutputPane(wx.Panel):

    def __init__(self, parent):

        ## new instance of message pane
        wx.Panel.__init__(self, parent=parent)
        r = wx.Display().GetGeometry()
        self.debug_list = ErrorListCtrl.ErrorListCtrl(parent=self, notebook=parent.notebook)
        self.debug_list.SetSize((r.Width, r.Height / 5))

    def show_output(self, list_of_errors):

        # display output onscreen
        self.debug_list.DeleteAllItems()
        self.debug_list.process_errors_string(list_of_errors)


class MessagePane(wx.Panel):

    def __init__(self, parent):

        ## new instance of message pane
        wx.Panel.__init__(self, parent=parent)
        r = wx.Display().GetGeometry()
        self.text_control = wx.TextCtrl(self, -1, "", wx.DefaultPosition, (r.Width, r.Height / 5), wx.NO_BORDER | wx.TE_MULTILINE)

    def show_message(self, text):

        # display a text message for user
        self.text_control.Clear()
        self.text_control.AppendText(text)

__author__ = 'dj'
