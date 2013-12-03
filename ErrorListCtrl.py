
# Control to display errors to user, and give us line number to each error

import wx
import re


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

        # split into lines to make our job easier
        pattern = re.compile("(.*)\(([0-9]*)\): error:")
        error_string = ""
        index = 0
        error_groups = pattern.split(errors_list)
        for e in error_groups:

            print e
            print "Check"

            """
            groups = pattern.findall(line)
            if groups:

                # we've found an error. add to the catalog
                self.InsertStringItem(index, "")
                self.SetStringItem(index, 1, str(groups[0][0]))
                self.SetStringItem(index, 2, str(groups[0][1]))
                index += 1
                error_string = ""

            else:
                error_string = error_string + line
                self.SetStringItem(index - 1, 0, error_string)
            """

    def error_entry_activated(self, event):

        print "test"


__author__ = 'dj'
