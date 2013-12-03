
## control displaying all files in a project

import wx
import wx.stc
import wx.lib.agw.aui


class ProjectBrowser(wx.ListCtrl):

    def __init__(self, object_browser, parent):

        ## new instance of object browser
        wx.ListCtrl.__init__(self, parent=parent, style=wx.LC_LIST)

        # we require reference to local object browser for communicating with the rest of the application
        self.object_browser = object_browser

        # when project file is activated use the file_activated event
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.file_activated)

    def file_activated(self, event):

        # open file to memory if not opened already
        # do this by calling the notebook
        file_name = event.GetText()
        self.object_browser.notebook.find_page(file_name)

    def update_files(self):

        # get file list from top window project object
        files = self.GetTopLevelParent().project.files
        self.DeleteAllItems()
        index = 0
        for file_name in files:
            self.InsertStringItem(index, file_name)
            index += 1

__author__ = 'dj'
