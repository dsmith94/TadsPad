
# object class for notebook - tabbed browser of code windows

import wx
import re
import wx.stc
import wx.lib.agw.aui as Aui
import Editor
import MessageSystem
import os.path
import codecs
import TadsParser
import ProjectFileSystem
import pickle
import embedded


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
        #self.Bind(Aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)

        # editor colors and text size
        self.colors = os.path.join(self.GetTopLevelParent().themes_path, 'Obsidian.xml')
        self.size = 12

        # the objects, classes, modifys and global tokens
        self.objects = {}
        self.classes = {}
        self.modifys = []
        self.global_tokens = {}

    def __getitem__(self, index):
        if index < self.GetPageCount():
            return self.GetPage(index)
        else:
            raise IndexError

    def load_classes(self, project):

        # load adv3lite/r worldmodel classes from file
        root = ProjectFileSystem.get_project_root()
        path = os.path.join(root, project.name)
        if os.path.exists(os.path.join(path, "classes.dat")) and os.path.exists(os.path.join(path, "globals.dat")):

            # it exists! load file so we get previously used class resources
            try:
                with open(os.path.join(path, "classes.dat"), 'rb') as the_file:
                    self.classes = pickle.load(the_file)
                with open(os.path.join(path, "globals.dat"), 'rb') as the_file:
                    self.global_tokens = pickle.load(the_file)
            except IOError:
                MessageSystem.error("Could not read file: " + path, path + " corrupted")
            return

        # no previous classes: load them
        self.classes = {}
        self.global_tokens = {}
        for l in project.libraries:
            parse_library(l, path, self.classes, self.modifys, self.global_tokens)

        # now that the heavy lifting is done, save the classes to file
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            with open(os.path.join(path, "classes.dat"), 'wb') as output:
                pickle.dump(self.classes, output)
            with open(os.path.join(path, "globals.dat"), 'wb') as output:
                pickle.dump(self.global_tokens, output)
        except IOError, e:
            MessageSystem.error("Could not save file: " + e.filename, "File write error")
            return

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

    def context_help(self):

        # ring up context senstive help by calling current page in code notebook
        try:
            index = self.GetSelection()
            page = self.GetPage(index)
        except IndexError, e:
            MessageSystem.error("Must have an open code window for context help system. ", "No Code Window Open")
        else:
            try:
                MessageSystem.show_message(page.editor.context_help())
            except:
                MessageSystem.show_message("No help found on that keyword. ")

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
        path = os.path.abspath(os.path.expanduser("~/Documents/TADS 3/" + self.GetTopLevelParent().project.name + "/"))
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

    def close_all(self):

        # close all opened pages
        for page in xrange(self.GetPageCount()):
            self.DeletePage(0)

    def new_page(self, name, the_project):

        # create a new page and add it to our notebook

        if name not in the_project.files:
            try:
                the_project.new_file(embedded.blank, name + ".t")
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
        tp.editor = Editor.EditorCtrl(tp, self)
        tp.editor.scheme.colors = self.colors
        tp.editor.scheme.size = self.size
        tp.editor.scheme.load_colors(tp.editor.scheme.colors)
        tp.editor.scheme.update_colors(tp.editor)
        tp.editor.SetEOLMode(wx.stc.STC_EOL_LF)
        tp.editor.ConvertEOLs(wx.stc.STC_EOL_LF)
        tp.SetSizerAndFit(sizer)
        sizer.Add(tp.editor, 1, wx.EXPAND | wx.ALL)
        tp.editor.filename = filename
        tp.editor.path = path
        try:
            with codecs.open(path + "/" + filename, 'rU', "utf-8") as code:
                text = code.read()
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

    def find_string(self, text, status):

        # find string in selected page
        try:
            index = self.GetSelection()
            page = self.GetPage(index)
        except:
            MessageSystem.error("No files opened, cannot search. ", "Search String Failure")
        else:
            n = page.editor.Text.count(text)
            status.SetStatusText("Found " + str(n) + " occurrences")
            page.editor.search_for(text)

    def replace_string(self, old, new, status):

        # replace string in selected page
        try:
            index = self.GetSelection()
            page = self.GetPage(index)
        except:
            MessageSystem.error("No files opened, cannot replace. ", "Replace String Failure")
        else:
            n = page.editor.Text.count(old)
            status.SetStatusText("Replaced 1 of " + str(n) + " occurrences")
            page.editor.replace_with(old, new)

    def replace_all_string(self, old, new, status):

        # replace all strings in selected page
        try:
            index = self.GetSelection()
            page = self.GetPage(index)
        except:
            MessageSystem.error("No files opened, cannot replace. ", "Replace String Failure")
        else:
            n = page.editor.Text.count(old)
            status.SetStatusText("Replaced all " + str(n) + " occurrences")
            page.editor.replace_all_with(old, new)

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

    def retheme(self):

        # re-theme all pages in this notebook with current theme values
        for page in self:
            page.editor.scheme.size = self.size
            page.editor.scheme.load_colors(self.colors)
            page.editor.scheme.update_colors(page.editor)


def parse_library(library, current_path, classes, modifys, global_tokens):

    # firstly, skip the system library
    if library == 'system':
        return

    # parse all classes/members in the presently selected world-model library
    sources_path = os.path.join(ProjectFileSystem.get_project_root(), 'extensions', 'adv3Lite')

    # attempt to read library
    try:
        with open(os.path.join(current_path, library + ".tl"), 'rU') as sources_file:
            sources_raw = sources_file.read()
    except IOError, e:
        MessageSystem.error("Could not load library source: file corrupted or not found " + e.filename,
                            "Library Read Error for " + library)
        return
    lines = sources_raw.split('\n')
    source_pattern = re.compile("source:\s(.*)")
    sources = []
    for line in lines:
        match = source_pattern.match(line)
        if match:
            sources.append(match.group(1))

    # we've collected all the source files from library, open each one
    load_dlg = wx.ProgressDialog('Building references, please wait...', 'Search source code', maximum=len(sources))
    for index, source in enumerate(sources):

        # if a path doesn't exist in the source string, add one
        if '/' in source:
            path = source + '.t'
        else:
            path = os.path.join(sources_path, source + ".t")

        # open and read source code file
        # only get globals from misc.t, there're all we need
        TadsParser.search(path, classes, modifys, global_tokens)

        # update dialog onscreen
        load_dlg.Update(index, source + ".t")

    load_dlg.Destroy()

    # now apply the modifys we just loaded
    [classes[m.name].members.update(m.members) for m in modifys if m.name in classes]

    # and our inherits
    for c in classes.values():
        c.inherits.extend(TadsParser.inherit_search(c, classes))


__author__ = 'dj'
