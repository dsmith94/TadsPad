
# object class for notebook - tabbed browser of code windows

import wx
import re
import wx.stc
import wx.lib.agw.aui as Aui
import Editor
import MessageSystem
import os.path
import TClass
import ProjectFileSystem
import pickle


class Notebook(Aui.AuiNotebook):
    """
    Notebook class, extended for our purposes
    """

    #----------------------------------------------------------------------
    def __init__(self, parent):
        Aui.AuiNotebook.__init__(self, parent=parent)
        self.default_style = Aui.AUI_NB_DEFAULT_STYLE | Aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER
        self.SetWindowStyleFlag(self.default_style)
        self.Bind(Aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close)
        self.Bind(Aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)

        # the objects and classes
        self.objects = list()
        self.classes = []

    def __getitem__(self, index):
        if index < self.GetPageCount():
            return self.GetPage(index)
        else:
            raise IndexError

    def load_classes(self, project):

        # load adv3lite worldmodel classes from file
        root = ProjectFileSystem.get_project_root()
        path = os.path.join(root, project.name)
        if os.path.exists(os.path.join(path, "classes.dat")):

            # it exists! load file so we get previously used class resources
            try:
                the_file = open(os.path.join(path, "classes.dat"), 'rb')
                self.classes = pickle.load(the_file)
                the_file.close()
            except IOError:
                MessageSystem.error("Could not read file: " + path, path + " corrupted")
            return

        # no previous classes: load them
        self.classes = parse_library(project.library)

        # now that the heavy lifting is done, save the classes to file
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            output = open(os.path.join(path, "classes.dat"), 'wb')
            pickle.dump(self.classes, output)
            output.close()
        except IOError, e:
            MessageSystem.error("Could not save file: " + e.filename, "File write error")

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

    def save_page(self):

        # save currently selected page
        index = self.GetSelection()
        page = self.GetPage(index)
        if page.editor.filename == "untitled":
            self.save_page_as()
            return
        if page.editor.save(page.editor.path, page.editor.filename):
            page.editor.saved = True
            self.SetPageText(index, page.editor.filename)

    def save_page_as(self):

        # create a dialog box allowing user to set filename
        path = os.path.abspath(os.path.expanduser("~/Documents/TADS 3/" + self.project_name + "/"))
        saveFileDialog = wx.FileDialog(self, "Save .t file", "", "", "t files (*.t)|*.t",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        else:
            index = self.GetSelection()
            page = self.GetPage(index)
            if page.editor.save(saveFileDialog.Path, saveFileDialog.Filename):
                page.editor.saved = True
                self.SetPageText(index, page.editor.filename)

    def save_all(self):

        # save all opened pages that have been modified
        # loop through all pages to do it
        index = 0
        for page in self:
            if page.editor.filename == "untitled":
                self.save_page_as()
            if page.editor.saved is not True:
                if page.editor.save(page.editor.path, page.editor.filename):
                    page.editor.saved = True
                    self.SetPageText(index, page.editor.filename)
            index += 1

    def new_page(self, name, the_project):

        # create a new page and add it to our notebook

        if name not in the_project.files:
            try:
                the_project.new_file("blank", name + ".t")
            except IOError, e:
                MessageSystem.error("Cannot add file: " + name, e.message)
            else:
                the_project.files.append(name + ".t")
                self.load_page(the_project.path, name + ".t")
        else:
            MessageSystem.error("Cannot add file: " + name + " - already in project", "File Name Disambiguation")

    def load_page(self, path, filename, line_number=0):

        # load page with filename passed above
        tp = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        tp.editor = Editor.EditorCtrl(self.classes, tp, self)
        tp.SetSizerAndFit(sizer)
        sizer.Add(tp.editor, 1, wx.EXPAND | wx.ALL)
        tp.editor.filename = filename
        tp.editor.path = path
        try:
            code = open(path + "/" + filename, 'rU')
            text = code.read()
            code.close()
        except IOError, e:
            MessageSystem.error("Not able to open file: " + e.filename, "File load error")
        else:
            text = text.replace("$FILENAME$", filename)
            tp.editor.SetText(text)
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
        self.load_page(self.GetTopLevelParent().project.path, name, line_number)

    def find_string(self, text):

        # find string in selected page
        try:
            index = self.GetSelection()
            page = self.GetPage(index)
        except:
            MessageSystem.error("No files opened, cannot search. ", "Search String Failure")
        else:
            page.editor.search_for(text)

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

    def spellcheck(self, project):

        # get opened editor page and check spelling
        index = self.GetSelection()
        if index >= 0:
            page = self.GetPage(index)
            page.editor.spellcheck(project)
        else:
            MessageSystem.error("Cannot spell-check without a valid TADS file open. ", "Spell check fail")


def parse_library(library):

    # parse all classes/members in the presently selected world-model library
    path_string = os.path.expanduser('~/Documents/TADS 3/extensions/adv3Lite')
    print (path_string)
    sources_file = open(os.path.join(path_string, library + ".tl"), 'rU')
    sources_raw = sources_file.read()
    sources_file.close()
    lines = sources_raw.split('\n')
    source_pattern = re.compile("source:\s(.*)")
    sources = []
    number_of_sources = 0
    sources_index = 0
    for line in lines:
        match = source_pattern.match(line)
        if match:
            sources.append(match.group(1))
            number_of_sources += 1

    classes = []
    load_dlg = wx.ProgressDialog('Building references, please wait...', 'Search source code', maximum=number_of_sources)
    for source in sources:
        print(os.path.join(path_string, source + ".t"))
        code_file = open(os.path.join(path_string, source + ".t"), 'rU')
        load_dlg.Update(sources_index, source + ".t")
        code = code_file.read()
        code_file.close()
        classes.extend(TClass.extract(code))
        sources_index += 1
    TClass.cross_reference(classes)
    load_dlg.Destroy()
    return classes


__author__ = 'dj'
