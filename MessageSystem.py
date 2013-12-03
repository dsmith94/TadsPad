#!/usr/bin/env python

## library to communicate messages to user

import wx
import webbrowser

Version_Number = "0.1"
About_Text = "TadsPad\nby dj\nVersion "

newBrowserTab = 2


# reference to main window
class MainWindow(object):

    instance = None

    @classmethod
    def get_instance(cls):
        return cls.instance


def library_reference(parent):

    # use web browser to display library reference
    url = "https://dl.dropboxusercontent.com/u/58348218/adv3Lite/docs/libref/index.html"
    webbrowser.open(url, new=newBrowserTab)


def tutorial_system(parent):

    # use web browser to display TADS 3 tutorial
    url = "https://dl.dropboxusercontent.com/u/58348218/adv3Lite/docs/tutorial/index.htm"
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
        panel = wx.Panel(self)
        panel.SetSizer(box_master)
        panel.Layout()


def show_message(text):

    # display message in message pane
    MainWindow.get_instance().show_message(text)


def error(message, title):

    # display message with title bar string
    dlg = wx.MessageDialog(None, message, title, wx.OK | wx.ICON_WARNING)
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


