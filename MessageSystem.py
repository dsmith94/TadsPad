#!/usr/bin/env python

## library to communicate messages to user

import wx
import os
import webbrowser
import ProjectFileSystem

Version_Number = u"0.5"
About_Text = u"TadsPad\nby dj\nVersion "

newBrowserTab = 2


# reference to main window
class MainWindow(object):

    instance = None

    @classmethod
    def get_instance(cls):
        return cls.instance


def bookshelf_system(parent):

    # use web browser to display TADS 3 adv3lite bookshelf
    path = ProjectFileSystem.get_project_root()
    url = os.path.join(path, 'extensions', 'adv3Lite', 'docs', 'index.htm')
    webbrowser.open(url, new=newBrowserTab)


def user_guide(parent):

    # use web browser to display TadsPad user's guide
    url = "http://dsmith94.github.io/TadsPad/"
    webbrowser.open(url, new=newBrowserTab)

def about_box(parent):

    # display message box describing software version info
    dlg = wx.MessageDialog(None, About_Text + Version_Number, "About TadsPad", wx.OK)
    dlg.ShowModal()
    dlg.Destroy()


class EntryWindow(wx.Dialog):
    def __init__(self, title):
        wx.Dialog.__init__(self, None, title=title)
        screen_geometry = wx.Display().GetGeometry()
        width = screen_geometry.Width / 6
        box_master = wx.BoxSizer(wx.VERTICAL)
        box_for_text = wx.BoxSizer(wx.VERTICAL)
        box_for_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.entry = wx.TextCtrl(self, size=(width, -1))
        box_for_text.Add(self.entry)
        ok_button = wx.Button(self, wx.ID_OK, "&OK")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        box_for_buttons.Add(ok_button, 0)
        box_for_buttons.Add(cancel_button)
        box_master.Add(box_for_text, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.Add(box_for_buttons, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.SetSizeHints(self)
        self.SetSizer(box_master)
        self.Layout()
        self.Fit()


def show_message(text):

    # display message in message pane
    MainWindow.get_instance().show_message(text)


def show_errors(errors_list):

    # display errors as a listctrl report
    MainWindow.get_instance().show_errors(errors_list)


def clear_errors():

    # clear errors on bottom panel
    MainWindow.get_instance().clear_errors()


def error(message, title):

    # display error message with title bar string
    dlg = wx.MessageDialog(None, message, title, wx.OK | wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()


def info(message, title):

    # display info message with title bar string
    dlg = wx.MessageDialog(None, message, title, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


def ask(message, title):

    # display message with title bar string
    dlg = wx.MessageDialog(None, message, title, wx.OK | wx.CANCEL | wx.ICON_QUESTION)
    result = dlg.ShowModal()
    dlg.Destroy()
    if result == wx.ID_OK:
        return True
    else:
        return False


__author__ = 'dj'


