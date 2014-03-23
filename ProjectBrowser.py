
## control displaying all files in a project

import wx
import os
import wx.stc
import wx.lib.agw.aui
import MessageSystem
import ProjectFileSystem


class ContextMenu(wx.Menu):

    # context menu for project browser

    def __init__(self, parent):
        super(ContextMenu, self).__init__()

        # build context menu
        self.rename = wx.MenuItem(self, wx.ID_ANY, 'Rename')
        self.AppendItem(self.rename)
        self.Bind(wx.EVT_MENU, parent.rename, self.rename)


class ProjectBrowser(wx.ListCtrl):

    def __init__(self, object_browser, parent):

        ## new instance of object browser
        wx.ListCtrl.__init__(self, parent=parent, style=wx.LC_LIST)

        # we require reference to local object browser for communicating with the rest of the application
        self.object_browser = object_browser

        # when project file is activated use the file_activated event
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.file_activated)

        # context menu for right click on files
        self.Bind(wx.EVT_RIGHT_DOWN, self.context_menu)

    def file_activated(self, event):

        # open file to memory if not opened already
        # do this by calling the notebook
        file_name = event.GetText()
        self.object_browser.notebook.find_page(file_name)

    def rename(self, event):

        # rename selected file in project browser
        index = self.GetFirstSelected()
        project = self.GetTopLevelParent().project
        files = project.files
        dialog = MessageSystem.EntryWindow("Rename " + files[index][:-2] + ":")
        result = dialog.ShowModal()
        path = os.path.join(ProjectFileSystem.get_project_root(), project.name)
        if result == wx.ID_OK:

            # remove funny chars that would make it an invalid filename
            name = dialog.entry.GetValue()
            name = ProjectFileSystem.remove_disallowed_filename_chars(name)

            # we've received go-ahead to rename file. make sure it is valid first
            if name in files:
                MessageSystem.error(name + " already exists in project! Rename operation failed.", "Duplicate file")
                return

            # okay, rename it
            name += ".t"
            os.rename(os.path.join(path, files[index]), os.path.join(path, name))
            for i in xrange(self.object_browser.notebook.GetPageCount()):
                if '*' in self.object_browser.notebook.GetPageText(i):
                    if self.object_browser.notebook.GetPageText(i).strip('* ') == files[index]:
                        self.object_browser.notebook.SetPageText(i, "* " + name)
                        self.object_browser.notebook.GetPage(i).editor.filename = name
                else:
                    if self.object_browser.notebook.GetPageText(i) == files[index]:
                        self.object_browser.notebook.SetPageText(i, name)
                        self.object_browser.notebook.GetPage(i).editor.filename = name
            files[index] = name
            self.object_browser.rebuild_object_catalog()
            self.update_files()

    def context_menu(self, event):

        # fire context menu when a file is selected
        if self.GetFirstSelected() > -1:
            self.PopupMenu(ContextMenu(self), event.GetPosition())


    def update_files(self):

        # get file list from top window project object
        files = self.GetTopLevelParent().project.files
        self.DeleteAllItems()
        index = 0
        for file_name in files:
            self.InsertStringItem(index, file_name)
            index += 1

__author__ = 'dj'
