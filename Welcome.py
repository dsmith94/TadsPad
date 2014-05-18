
# welcome to tadspad box - used to get user input when starting tadspad (w/o a prev project found)

import wx
import embedded
import random


def get_tips():

    # load tips from default location (same dir)
    tips = embedded.tips.split('\n')
    random.shuffle(tips)
    return "Tip of the day: \n" + tips[0]

class Box(wx.Dialog):
    def __init__(self, preferences):
        wx.Dialog.__init__(self, None, title="Welcome to TadsPad!")

        # return file name of project to load
        self.file_string = None

        # create welcome to tads box
        screen_geometry = wx.Display().GetGeometry()
        self.width = screen_geometry.Width / 2
        self.height = screen_geometry.Width / 2
        contents = wx.BoxSizer(wx.VERTICAL)
        box_for_buttons = wx.BoxSizer(wx.HORIZONTAL)
        tips_box = wx.StaticText(parent=self, label=get_tips())
        tips_box.Wrap(self.width / 2)
        tips_box.Font = wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        tips_box.SetBackgroundColour('#FFFACD')
        open_button = wx.Button(self, wx.ID_OPEN, "&Open Project")
        open_button.Bind(wx.EVT_BUTTON, self.shutdown, id=wx.ID_OPEN)
        new_button = wx.Button(self, wx.ID_NEW, "&Create New Project")
        new_button.Bind(wx.EVT_BUTTON, self.shutdown, id=wx.ID_NEW)
        tutorial_button = wx.Button(self, wx.ID_HELP, "&First Time Tutorial")
        tutorial_button.Bind(wx.EVT_BUTTON, self.shutdown, id=wx.ID_HELP)
        contents.Add(tips_box, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        box_for_buttons.Add(new_button, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        box_for_buttons.Add(open_button, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        box_for_buttons.Add(tutorial_button, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        contents.Add(box_for_buttons, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        self.SetSizer(contents)
        self.Fit()

    def shutdown(self, event):

        # close this form
        self.EndModal(event.Id)

__author__ = 'dj'
