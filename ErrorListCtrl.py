
# Control to display errors to user, and give us line number to each error

import wx
import re
import os


class ErrorListCtrl(wx.ListCtrl):

    def __init__(self, parent):

        ## new instance of error list control
        wx.ListCtrl.__init__(self, parent=parent, style=wx.LC_REPORT)

        # when object is activated use the ObjectActivated event
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.error_entry_activated)

        # finalize columns and finish
        r = wx.Display().GetGeometry()
        self.InsertColumn(0, "Error", width=r.Width / 2)
        self.InsertColumn(1, "file")
        self.InsertColumn(2, "line")

    def process_errors_string(self, errors_list):

        # process a string containing errors from tads compiler
        self.DeleteAllItems()

        # clean up errors string and search
        errors_list = errors_list.replace("\r\n", "\n")
        errors_list = errors_list.replace("\r", "\n")
        errors_list = re.sub("\t.*", "\n", errors_list)
        error_groups = re.findall("\n(.*)\((\d*)\):\serror: \n(.*)\n\n", errors_list, flags=re.DOTALL)

        # first group is the file, second is the linenumber, third is the error itself
        index = 0
        for e in error_groups:
            self.InsertStringItem(index, e[2])
            self.SetStringItem(index, 1, os.path.basename(e[0]))
            self.SetStringItem(index, 2, e[1])
            index += 1

    def error_entry_activated(self, event):

        print "test"


__author__ = 'dj'
