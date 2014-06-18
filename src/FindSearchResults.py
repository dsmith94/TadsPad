#
#   FindSearchResults - a simple GUI to show search results in all files from FindReplaceWindow in a project
#

import wx
import os
import MessageSystem
import codecs
import TadsParser


class Window(wx.Frame):
    def __init__(self, search_string, notebook, project, in_strings, case_sensitive):

        """
        Create new window for Find search results
        """

        wx.Frame.__init__(self, None, title="Find " + search_string + " in Project " + project.name)
        r = wx.Display().GetGeometry()
        self.SetSize(wx.Size(r.Width / 2, r.Height / 2))
        self.results = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.results.InsertColumn(0, "Context", width=r.Width / 2)
        self.results.InsertColumn(1, "File Name", width=r.Width / 4)
        self.results.InsertColumn(2, "Line Number", width=r.Width / 4)
        self.results.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.result_activated)
        self.project = project
        self.search_string = search_string
        self.notebook = notebook
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.results, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(sizer)
        self.Fit()
        self.Maximize()
        self.in_strings = in_strings
        self.case_sensitive = case_sensitive
        self.search()

    def result_activated(self, event):

        # show find result in editor
        index = event.GetIndex()
        filename = str(self.results.GetItem(index, 1).GetText())
        line = int(self.results.GetItem(index, 2).GetText())
        self.notebook.find_page(filename, line)
        self.Close()

    def search(self):

        """
        search for "search_string" in project files
        """

        files = self.project.files
        path = self.project.path
        current_result = 0
        for file_name in files:
            try:
                with codecs.open(path + "/" + file_name, 'rU', "utf-8") as f:
                    file_contents = f.read()

                    # search only in strings if in_strings flag is true
                    if self.in_strings:
                        file_contents = TadsParser.extract_strings(file_contents)

            except IOError, e:
                MessageSystem.error("Could not load file: " + e.filename, "File read error")

            # if the file can be read, search line by line for search string
            else:
                if file_contents:
                    for index, line in enumerate(file_contents.split(u"\n")):

                        # if we have search string in file, add to results
                        if self.case_sensitive:
                            if self.search_string in line:
                                self.results.InsertStringItem(current_result, line)
                                self.results.SetStringItem(current_result, 1, file_name)
                                self.results.SetStringItem(current_result, 2, str(index))
                                current_result += 1
                        else:
                            if self.search_string.lower() in line.lower():
                                self.results.InsertStringItem(current_result, line)
                                self.results.SetStringItem(current_result, 1, file_name)
                                self.results.SetStringItem(current_result, 2, str(index))
                                current_result += 1


__author__ = 'dj'
