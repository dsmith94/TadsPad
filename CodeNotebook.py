
# object class for notebook - tabbed browser of code windows

import wx
import re
import wx.stc
import wx.lib.agw.aui
import Editor
import MessageSystem
import os.path
import glob
import ObjectBrowser


class Notebook(wx.lib.agw.aui.AuiNotebook):
    """
    Notebook class, extended for our purposes
    """

    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.lib.agw.aui.AuiNotebook.__init__(self, parent=parent)
        self.default_style = \
            wx.lib.agw.aui.AUI_NB_DEFAULT_STYLE | wx.lib.agw.aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER
        self.SetWindowStyleFlag(self.default_style)
        self.project_name = "unnamed project"
        self.auto_code_dictionary = {}
        self.auto_code_tooltips = {}
        self.Bind(wx.lib.agw.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close)
        self.Bind(wx.lib.agw.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        self.get_auto_code_data()

        # the objects!
        self.objects = list()

    def __getitem__(self, index):
        if index < self.GetPageCount():
            return self.GetPage(index)
        else:
            raise IndexError

    def close_all(self):

        # close all opened pages
        while self.GetPageCount() > 0:
            self.DeletePage(0)

    def cut(self):

        # cut with clipboard
        index = self.GetSelection()
        page = self.GetPage(index)
        page.editor.Cut()

    def copy(self):

        # copy with clipboard
        index = self.GetSelection()
        page = self.GetPage(index)
        page.editor.Copy()

    def paste(self):

        # paste with clipboard
        index = self.GetSelection()
        page = self.GetPage(index)
        page.editor.Paste()

    def undo(self):

        #undo last text adjustment
        index = self.GetSelection()
        page = self.GetPage(index)
        page.editor.Undo()

    def redo(self):

        #redo last text adjustment
        index = self.GetSelection()
        page = self.GetPage(index)
        page.editor.Redo()

    def get_unsaved_pages(self):

        # return list of pages not yet saved

        return_value = []
        for page in self:
            if page.editor.saved is False:
                return_value.append(page.editor.filename)
        return return_value

    def save_page(self, object_browser):

        # save currently selected page
        index = self.GetSelection()
        page = self.GetPage(index)
        if page.editor.filename == "untitled":
            self.save_page_as(object_browser)
            return
        if page.editor.save(page.editor.path, page.editor.filename, object_browser):
            page.editor.saved = True
            self.SetPageText(index, page.editor.filename)

    def save_page_as(self, object_browser):

        # create a dialog box allowing user to set filename
        path = os.path.abspath(os.path.expanduser("~/Documents/TADS 3/" + self.project_name + "/"))
        saveFileDialog = wx.FileDialog(self, "Save .t file", "", "", "t files (*.t)|*.t",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        else:
            index = self.GetSelection()
            page = self.GetPage(index)
            if page.editor.save(saveFileDialog.Path, saveFileDialog.Filename, object_browser):
                page.editor.saved = True
                self.SetPageText(index, page.editor.filename)

    def save_all(self, object_browser):

        # save all opened pages that have been modified
        # loop through all pages to do it
        index = 0
        for page in self:
            if page.editor.filename == "untitled":
                self.save_page_as(object_browser)
            if page.editor.saved is not True:
                if page.editor.save(page.editor.path, page.editor.filename, object_browser):
                    page.editor.saved = True
                    self.SetPageText(index, page.editor.filename)
            index += 1

    def new_page(self, name, the_project):

        # create a new page and add it to our notebook

        try:
            from shutil import copyfile
            copyfile("./blank.tmp", the_project.path + "/" + name + ".t")
            the_project.files.append(name + ".t")
            self.load_page(the_project.path, name + ".t", the_project.title)
        except IOError, e:
            MessageSystem.error("Unable to write new file: " + name + ".t", "No new file added - " + e.filename)

    def load_page(self, path, filename, title, line_number=0):

        # load page with filename passed above
        tp = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        tp.editor = Editor.EditorCtrl(self.auto_code_tooltips, tp, self.auto_code_dictionary, self)
        tp.SetSizerAndFit(sizer)
        sizer.Add(tp.editor, 1, wx.EXPAND | wx.ALL)
        tp.editor.filename = filename
        tp.editor.path = path
        try:
            code = open(path + "/" + filename, 'r')
            tp.editor.SetText(code.read().replace("$FILENAME$", filename).replace("$TITLE$", title))
            code.close()
        except IOError, e:
            MessageSystem.error("Not able to open file: " + e.filename, "File load error")
        tp.editor.Bind(wx.stc.EVT_STC_CHANGE, self.on_text_changed)
        self.AddPage(tp, tp.editor.filename)
        self.SetSelection(self.GetPageCount() - 1)
        tp.SetFocus()
        tp.editor.GotoLine(line_number)
        tp.editor.ScrollToLine(line_number - 1)

    def find_page(self, name, line_number=0):

        # find a loaded page by it's name, passed above, and highlight a line number if provided
        index = 0
        for panel in self:
            if panel.editor.filename == name:
                self.SetSelection(index)
                panel.SetFocus()
                panel.editor.GotoLine(line_number)
                panel.editor.ScrollToLine(line_number - 1)
                return
            index += 1

        # try loading it from memory if we can't find it already open
        self.load_page(self.GetTopLevelParent().project.path, name,
                       self.GetTopLevelParent().project.title, line_number)

    def highlight_error(self, name, line_number, error_string):

        # scroll through opened pages, find page with the name passed above, highlight line
        # number and open call tip with error string
        index = 0
        for panel in self:
            if panel.editor.filename == name:
                panel.editor.CallTipShow(panel.editor.GetLineEndPosition(line_number), error_string)
                return
            index += 1

    def on_text_changed(self, event):

        # when page is changed, unsaved is new status of document
        index = self.GetSelection()
        page = self.GetPage(index)
        page.editor.saved = False
        self.SetPageText(index, "* " + self.GetPageText(index).strip("* "))     # show * by filename

    def on_page_changed(self, event):

        # when notebook page selection is changed, refresh object browser
        self.GetTopLevelParent().object_browser.rebuild_object_catalog()

    def on_page_close(self, event):

        # before page close, check that we are saved
        index = event.GetSelection()
        page = self.GetPage(index)
        if page.editor.saved is False:
            if MessageSystem.ask("Really close " + page.editor.filename + "?", "Unsaved data") is False:
                event.Veto()

    def get_auto_code_data(self):

        # load all documents that give us data on classes
        # then parse into code entries and definitions

        list_of_docs = glob.glob("./auto/*.inf")
        for doc in list_of_docs:
            doc_file = open(doc, 'r')
            name_of_class = doc_file.name[7:-4]
            code_definitions_list = doc_file.read().replace("\r", "").split("\n\n")
            for definition in code_definitions_list:
                processed_definition = definition.split('\n', 1)
                get_new_list_for_class = ""
                if name_of_class in self.auto_code_dictionary:
                    get_new_list_for_class = str(self.auto_code_dictionary[name_of_class]) + processed_definition[0] + "^"
                self.auto_code_dictionary.update({name_of_class: get_new_list_for_class})
                self.auto_code_dictionary[name_of_class].strip(" ")
                if processed_definition[0] not in self.auto_code_tooltips:
                    self.auto_code_tooltips.update({processed_definition[0]: processed_definition[1]})
                if processed_definition[1] != "no description available":
                    self.auto_code_tooltips.update({processed_definition[0]: processed_definition[1]})
            doc_file.close()

        # now that we have the definitions, parse the subclass files to figure out where all the subclassed
        # properites go
        list_of_superclasses = glob.glob("./auto/*.sub")
        for superclass_file in list_of_superclasses:
            superclass_data = open(superclass_file, 'r')
            name_of_superclass = superclass_file[7:-4]
            subclass_list = superclass_data.read().replace("\r", "").split("\n")
            for subclass in subclass_list:
                if subclass in self.auto_code_dictionary:
                    self.auto_code_dictionary[subclass] += self.auto_code_dictionary[name_of_superclass]
            superclass_data.close()


__author__ = 'dj'
