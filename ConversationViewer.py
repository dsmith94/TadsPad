
# simple window to view what topics have/have not been added to a given actor/agenda

import wx
import ProjectFileSystem
import TClass


class Window(wx.Frame):
    def __init__(self, project):
        wx.Frame.__init__(self, None, title="Conversation Viewer")

        r = wx.Display().GetGeometry()
        self.SetSize(wx.Size(r.Width / 2, r.Height / 2))
        transcript_ctrl = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        transcript_ctrl.InsertColumn(0, "Command List", width=r.Width / 4)
        transcript_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.command_activated)
        index = 0
        self.terp = terp
        self.tads3path = tads3path
        self.transcript = process_transcript(project.path)
        self.project = project
        self.terminal = terminal
        for command in self.transcript:
            transcript_ctrl.InsertStringItem(index, command)
            index += 1
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(transcript_ctrl, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(sizer)
        self.Fit()



__author__ = 'dj'
