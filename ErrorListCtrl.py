
# Control to display errors to user, and give us line number to each error

import wx
import re
import os


class ErrorListCtrl(wx.ListCtrl):

    def __init__(self, parent, notebook):

        ## new instance of error list control
        wx.ListCtrl.__init__(self, parent=parent, style=wx.LC_REPORT)

        # when entry is activated use the error entry activated event
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.error_entry_activated)

        # remember where the notebook is in memory
        self.notebook = notebook

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

        # first in list is the file, second is the linenumber, third is the error itself
        index = 0
        for e in error_groups:
            self.InsertStringItem(index, "\n" + e[2])
            self.SetStringItem(index, 1, os.path.basename(e[0]))
            self.SetStringItem(index, 2, e[1])
            index += 1

    def error_entry_activated(self, event):

        # we've got an error entry selected by user, highlight it in the notebook
        entry = event.GetEventObject()
        index = event.GetIndex()
        file_name = str(entry.GetItem(index, 1).GetText())
        line_number = int(entry.GetItem(index, 2).GetText())
        error_text = str(entry.GetItem(index, 0).GetText())
        self.notebook.find_page(file_name, line_number)
        self.notebook.highlight_error(file_name, line_number, error_text)

__author__ = 'dj'
