
# dialog for reconfiguring library setup used for games

import wx
import ProjectFileSystem
import os


class Dialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, title="Re-configure Library Setup")

        # get extensions
        path = os.path.join(ProjectFileSystem.get_project_root(), "extensions", "adv3Lite", "extensions")
        filetree = os.walk(path, True)
        extensions = ProjectFileSystem.get_differences_lite()
        for root, dirs, files in filetree:
            for f in files:
                if f[-2:] == '.t':
                    extensions.append('extensions/' + f[:-2])

        # build ui
        screen_geometry = wx.Display().GetGeometry()
        width = screen_geometry.Width / 5
        box_master = wx.BoxSizer(wx.VERTICAL)
        box_for_text = wx.BoxSizer(wx.VERTICAL)
        box_for_buttons = wx.BoxSizer(wx.HORIZONTAL)
        box_for_custom = wx.BoxSizer(wx.VERTICAL)
        self.lite = wx.RadioButton(self, -1, 'adv3Lite', style=wx.RB_GROUP)
        self.lite.Bind(wx.EVT_RADIOBUTTON, self.custom_checked, id=wx.ID_ANY)
        self.liter = wx.RadioButton(self, -1, 'adv3Liter')
        self.liter.Bind(wx.EVT_RADIOBUTTON, self.custom_checked, id=wx.ID_ANY)
        self.custom = wx.RadioButton(self, -1, 'Custom')
        self.custom.Bind(wx.EVT_RADIOBUTTON, self.custom_checked, id=wx.ID_ANY)
        self.extensions = wx.CheckListBox(self, id=-1, choices=extensions)
        self.extensions.Enabled = False
        box_for_custom.Add(self.custom)
        box_for_custom.Add(self.extensions)
        box_for_text.Add(wx.StaticText(self, label="Choose Library:    "))
        box_for_text.Add(self.lite)
        box_for_text.Add(self.liter)
        box_for_text.Add(box_for_custom)
        self.ok_button = wx.Button(self, wx.ID_OK, "&OK")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        box_for_buttons.Add(self.ok_button, 0)
        box_for_buttons.Add(cancel_button)
        box_master.Add(box_for_text, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.Add(box_for_buttons, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.SetSizeHints(self)
        box_master.Layout()
        self.SetSizer(box_master)
        self.Fit()
        self.Update()

    def custom_checked(self, event):

        # when custom checkbox is clicked, ungray (or gray) extensions box
        self.extensions.Enabled = self.custom.GetValue()


__author__ = 'dj'
