

# theme editor box

import os
import wx
import MessageSystem


class Box(wx.Dialog):
    def __init__(self, style, path, size=12):
        wx.Dialog.__init__(self, None, title="Theme Editor")

        # theme dialog contents
        screen_geometry = wx.Display().GetGeometry()
        self.width = screen_geometry.Width / 2
        self.height = screen_geometry.Width / 2
        contents = wx.BoxSizer(wx.VERTICAL)
        self.text_size = wx.StaticText(parent=self, label="Text Size: %s" % size)
        self.slider = wx.Slider(self, value=size, minValue=2, maxValue=46)
        self.slider.Bind(wx.EVT_SLIDER, self.change_size, id=wx.ID_ANY)
        self.theme = wx.TextCtrl(self)
        self.theme.Value = style
        self.path = path
        theme_button = wx.Button(self, wx.ID_FILE, "&Load Color XML...")
        theme_button.Bind(wx.EVT_BUTTON, self.load_colors, id=wx.ID_FILE)
        contents.Add(self.text_size, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        contents.Add(self.slider, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        contents.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        contents.Add(wx.StaticText(parent=self, label="Color Scheme:"), 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        contents.Add(self.theme, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        contents.Add(theme_button, 0, wx.EXPAND | wx.ALL, border=screen_geometry.Width / 100)
        box_for_buttons = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, wx.ID_OK, "&Ok")
        ok_button.Bind(wx.EVT_BUTTON, self.shutdown, id=wx.ID_OK)
        cancel_button = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        cancel_button.Bind(wx.EVT_BUTTON, self.shutdown, id=wx.ID_CANCEL)
        box_for_buttons.Add(ok_button, 0, wx.ALL, border=screen_geometry.Width / 100)
        box_for_buttons.Add(cancel_button, 0, wx.ALL, border=screen_geometry.Width / 100)
        contents.Add(box_for_buttons)
        contents.SetSizeHints(self)
        self.SetSizer(contents)
        self.Fit()

    def change_size(self, event):

        # change font size on label display
        self.text_size.SetLabel("Text Size: %s" % self.slider.Value)

    def shutdown(self, event):

        # close this form
        self.EndModal(event.Id)

    def load_colors(self, event):

        # show file open dialog

        dialog = wx.FileDialog(self, "Load Eclipse Color Scheme", "", "", "xml files (*.xml)|*.xml", wx.FD_OPEN)
        dialog.Path = self.path
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        else:
            path = dialog.Path
            if os.path.exists(path):
                self.theme.SetValue(path)
            else:
                MessageSystem.error("File not found: " + path, "Cannot Load XML")


__author__ = 'dj'
