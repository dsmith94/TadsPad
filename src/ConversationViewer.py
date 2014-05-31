
# simple window to view what topics have/have not been added to a given actor/agenda

# i've decided to shelve this code for now, because conversations are really hard to parse
# maybe later

import wx
import ProjectFileSystem
import TadsParser


class Window(wx.Frame):
    def __init__(self, objects):
        wx.Frame.__init__(self, None, title="Conversation Viewer")

        r = wx.Display().GetGeometry()
        self.SetSize(wx.Size(r.Width / 2, r.Height / 2))
        self.objects = objects
        self.actor = None
        self.state = None
        self.actors = {}
        [self.actors.update({a.name: a}) for a in self.objects if 'Actor' in a.inherits]
        self.states = []
        self.topics = [t for t in objects for i in t.inherits if 'topic' in i.lower()]
        self.actor_ctrl = wx.ComboBox(self, choices=[a.name for a in self.actors], style=wx.CB_READONLY)
        self.states_ctrl = wx.ComboBox(self, choices=self.states, style=wx.CB_READONLY)
        self.topic_ctrl = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.topic_ctrl.InsertColumn(0, "Has Topic:", width=r.Width / 4)
        self.not_ctrl = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.not_ctrl.InsertColumn(0, "Not Yet Implemented:", width=r.Width / 4)
        self.actor_ctrl.Bind(wx.EVT_COMBOBOX, self.update_states)
        self.states_ctrl.Bind(wx.EVT_COMBOBOX, self.update_topics)
        list_sizer = wx.BoxSizer(wx.HORIZONTAL)
        list_sizer.Add(self.topic_ctrl, 0, wx.EXPAND | wx.ALL, border=r.Width / 50)
        list_sizer.Add(self.not_ctrl, 0, wx.EXPAND | wx.ALL, border=r.Width / 50)
        master = wx.BoxSizer(wx.VERTICAL)
        master.Add(self.actor_ctrl, 0, wx.EXPAND | wx.ALL, border=r.Width / 50)
        master.Add(self.states_ctrl, 0, wx.EXPAND | wx.ALL, border=r.Width / 50)
        master.Add(list_sizer)
        self.SetSizer(master)
        self.Fit()

    def update_states(self, event):

        # update states for selected actor
        self.state = None
        name = self.actor_ctrl.GetValue()
        if name in self.actors:
            self.actor = self.actors[name]
            self.states = [o for o in self.objects if actor.name in o.parent if 'ActorState' in o.inherits]
            self.states_ctrl.AppendText('None')
            for s in self.states:
                self.states_ctrl.AppendText(s.name)
        else:
            self.actor_ctrl.Clear()

    def update_topics(self, event):

        # update topics in list controls onscreen
        if self.actor is None or self.state is None:
            return
        implemented = []
        not_implemented = self.objects
        for t in self.topics:


                for command in self.transcript:
            topic_ctrl.InsertStringItem(index, command)
            index += 1


__author__ = 'dj'
