#!/usr/bin/python

#
#   Primary source file for TadsPad
#   written by dj
#

import wx
import BuildMainUi
import TranscriptView
import MessageSystem
import BuildProcess
import ProjectFileSystem
import FindReplaceWindow
import PrefsEditWindow
import ThemeDialog
import Welcome
import pickle
import os
import sys
import shutil


def is_64_windows():
    return 'PROGRAMFILES(X86)' in os.environ


def get_program_files_32():
    if is_64_windows():
        return os.environ['PROGRAMFILES(X86)']
    else:
        return os.environ['PROGRAMFILES']


def get_terminal():

    # determine terminal by platform
    if sys.platform == 'Darwin':
        return "Terminal"
    if sys.platform == 'Linux':
        distro = sys.platform.linux_distribution()
        red_hats = 'Arch', 'Fedora', 'PCLinuxOS', 'SuSE'
        if red_hats in distro:
            return 'xterm'
        return "x-terminal-emulator"
    return "xterm"


class MainWindow(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title)

        # list to gray certain menu items when no project loaded
        self.grayable = []

        # user preferences - blank by default, until we load something in them
        self.preferences = {}

        # find config data and default prefs, according to current platform
        self.config_path = ""
        if sys.platform == 'win32':
            self.config_path = os.path.join(os.getenv('APPDATA'), "tadspad", "prefs.dat")
            self.preferences["tadspath"] = os.path.join(get_program_files_32(), "TADS 3", "t3make.exe")
            self.preferences["terp"] = os.path.join(get_program_files_32(), "TADS 3", "htmlt3.exe")
        else:
            self.config_path = os.path.join(os.path.expanduser("~"), "tadspad", "prefs.dat")
            self.preferences["tadspath"] = "t3make"
            self.preferences["terp"] = "frobtads"

        # figure out default terminal by platform
        self.preferences["terminal"] = get_terminal()

        # build main user interface
        BuildMainUi.init(self)
        self.Title = "TadsPad"
        self.Bind(wx.EVT_CLOSE, self.on_quit)

        # by default, with no project loaded, most menu items are grayed out
        self.menus(False)

        # pass reference to this window to the message subsystem
        MessageSystem.MainWindow.instance = self

        # load last project
        self.project = None
        self.on_load()

    def menus(self, enabled):

        # enable or disable menus
        # usually we disable menu items when no project is loaded
        for m in self.grayable:
            m.Enable(enabled)

    def undo(self, event):

        # undo last adjustment in text in the notebook
        self.notebook.undo()

    def cut(self, event):

        # clipboard cut
        self.notebook.cut()

    def copy(self, event):

        # clipboard copy
        self.notebook.copy()

    def paste(self, event):

        # clipboard paste
        self.notebook.paste()

    def redo(self, event):

        # Redo last adjustment in text in the notebook
        self.notebook.redo()

    def find_replace(self, event):

        # find/replace window
        fr = FindReplaceWindow.FindReplaceWindow(self.project, self.notebook)
        fr.Show()

    def theme_window(self, event):

        # edit editor theme with dialog
        box = ThemeDialog.Box(self.notebook.colors, self.notebook.size)
        result = box.ShowModal()
        if result == wx.ID_OK:
            self.notebook.colors = box.theme.Value
            self.notebook.size = box.slider.Value
            self.notebook.retheme()

    def new_page(self, event):

        # add new file to project (and query user for the name of the file)
        dlg = MessageSystem.EntryWindow("Please enter name of new file to add to project:")
        result = dlg.ShowModal()
        if result == wx.ID_OK:

            # clean up name for use as a filename
            new_name = ProjectFileSystem.remove_disallowed_filename_chars(dlg.entry.GetValue())

            # name is valid, so continue
            if new_name != "":
                self.notebook.new_page(new_name, self.project)
                self.project_browser.update_files()

            # name is not valid, forget it
            else:
                MessageSystem.error("No valid name selected - no new project file added.", "Sorry!")

    def on_load(self):

        # when loading tadspad, check for existence of program preferences
        if os.path.exists(self.config_path):

            # it exists! load file so we get prefs from last time
            try:
                the_file = open(self.config_path, 'rb')
                self.preferences = pickle.load(the_file)
                the_file.close()
            except IOError:
                MessageSystem.error("Could not read file: " + self.config_path, self.config_path + " corrupted")
            else:
                self.load_preferences()
                return

        # no pref.conf, it's our first time loading tadspad
        self.first_time_load()

    def load_preferences(self):

        # load program preferences from file
        # chief here is the last opened project
        if self.preferences["last project"]:
            self.project = ProjectFileSystem.load_project(self.preferences["last project"])
        else:
            self.first_time_load()
        self.mgr.LoadPerspective(self.preferences["layout"])
        if "colors" in self.preferences:
            self.notebook.colors = self.preferences["colors"]
        if "size" in self.preferences:
            self.notebook.size = int(self.preferences["size"])
        if self.project:
            self.notebook.load_classes(self.project)
            self.object_browser.rebuild_object_catalog()
            self.project_browser.update_files()
            self.Title = "TadsPad - " + self.project.name
            self.menus(True)

    def first_time_load(self):

        # first time loading tadspad, give user some options
        box = Welcome.Box(self.preferences).ShowModal()
        if box == wx.ID_NEW:

            # new project selected
            self.new_project_window()

        if box == wx.ID_OPEN:

            # load project from file
            # this triggers the open project menu function, so give it the button event instead of normal menu event
            self.load_project(wx.EVT_BUTTON)

        if box == wx.ID_HELP:

            # open tadspad tutorial
            print('no help yet')

    def save_preferences(self):

        # save preferences to file before quit
        path = os.path.dirname(self.config_path)
        self.preferences["layout"] = self.mgr.SavePerspective()
        if not os.path.exists(path):
            os.makedirs(path)
        self.preferences.update({"colors": self.notebook.colors})
        self.preferences.update({"size": self.notebook.size})
        if self.project:
            self.preferences.update({"last project": os.path.join(self.project.path, self.project.filename)})
            self.project.write()
        else:
            self.preferences.update({"last project": None})
        try:
            output = open(self.config_path, 'wb')
            pickle.dump(self.preferences, output)
            output.close()
        except IOError, e:
            MessageSystem.error("Could not save preferences: " + e.filename, "File write error")

    def on_quit(self, event):
        unsaved_pages = self.notebook.get_unsaved_pages()
        appendix_message = ""
        if len(unsaved_pages) != 0:
            appendix_message += "\n"
            for page in unsaved_pages:
                appendix_message += "\n   " + page
            appendix_message = appendix_message + "\n\n" + "is not yet saved!"
        if MessageSystem.ask("Really quit? " + appendix_message, "Exiting TadsPad"):

            # save preferences to file before quit
            self.save_preferences()
            wx.App.Exit(app)

    def close_project(self, event):

        # check unsaved pages first
        unsaved_pages = self.notebook.get_unsaved_pages()
        appendix_message = ""
        if len(unsaved_pages) != 0:
            appendix_message += "\n"
            for page in unsaved_pages:
                appendix_message += "\n   " + page
            appendix_message = appendix_message + "\n\n" + "is not yet saved!"
        if MessageSystem.ask("Really close project? " + appendix_message, "Project files unsaved"):

            # close current tadspad project
            self.project = None
            self.object_browser.DeleteAllItems()
            self.project_browser.DeleteAllItems()
            self.Title = "TadsPad"
            self.menus(False)
            self.notebook.close_all()

    def debug_project(self, event):

        # compile and run current tads story
        # to do this, make a new thread
        process = BuildProcess.CompileGame
        BuildProcess.run(process, self.project, self.preferences["terp"], self.preferences["tadspath"], flags=' -v -d ',
                         terminal=self.preferences["terminal"])

    def rebuild_project(self, event):

        # compile and rebuild tads project
        # to do this, make a new thread
        process = BuildProcess.CompileGame
        BuildProcess.run(process, self.project, self.preferences["terp"], self.preferences["tadspath"],
                         flags=' -v -d -a ', terminal=self.preferences["terminal"])

    def finalize_project(self, event):

        # compile final version of tads game project
        # to do this, make a new thread
        process = BuildProcess.CompileGame
        BuildProcess.run(process, self.project, self.preferences["terp"], self.preferences["tadspath"], flags=' -a ',
                         terminal=self.preferences["terminal"])

    def load_project(self, event):

        # load previously worked on project
        path = os.path.abspath(os.path.join(os.path.expanduser("~/Documents"), "TADS 3/"))
        dialog = wx.FileDialog(self, "Load .t3m file", "", "", "t files (*.t3m)|*.t3m", wx.FD_OPEN)
        dialog.Path = path + "/"
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        else:
            self.notebook.close_all()
            self.project = ProjectFileSystem.load_project(dialog.Path)
            if self.project:
                self.project_browser.update_files()
                self.object_browser.rebuild_object_catalog()
                self.notebook.load_classes(self.project)
                self.Title = "TadsPad - " + self.project.name
                self.menus(True)

    def save_page(self, event):

        # save this page
        self.notebook.save_page()
        self.object_browser.rebuild_object_catalog()
        self.project_browser.update_files()

    def save_page_as(self, event):

        # save this page under another filename
        self.notebook.save_page_as()
        self.object_browser.rebuild_object_catalog()
        self.project_browser.update_files()

    def save_all(self, event):

        # save all modified files
        self.notebook.save_all()
        self.object_browser.rebuild_object_catalog()
        self.project_browser.update_files()

    def new_project(self, event):

        # new project, but don't insist
        self.new_project_window()

    def show_message(self, text):

        # display text in message pane
        self.message_pane.show_message(text)
        self.message_book.Update()

    def show_errors(self, text):

        # display errors text in message pane
        self.message_book.SetSelection(1)
        self.output_pane.show_output(text)
        self.message_book.Update()

    def clear_errors(self):

        # clear errors in error panel
        self.message_book.SetSelection(1)
        self.output_pane.clear_output()
        self.message_book.Update()

    def toggle_messages(self, event):

        # toggle messages pane
        if self.mgr.GetPane('messages').IsShown():
            self.mgr.GetPane('messages').Hide()
        else:
            self.mgr.GetPane('messages').Show()
        self.mgr.Update()

    def toggle_objects(self, event):

        # toggle messages pane
        if self.mgr.GetPane('project').IsShown():
            self.mgr.GetPane('project').Hide()
        else:
            self.mgr.GetPane('project').Show()
        self.mgr.Update()

    def new_project_window(self):

        # create a new project.

        # call the new project routine from library
        self.project = ProjectFileSystem.TadsProject()
        dlg = ProjectFileSystem.NewProjectWindow()
        result = dlg.ShowModal()
        get_name = ""
        get_title = ""
        get_author = ""
        get_library = ['system']
        get_email = ""
        get_htmldesc = ""
        get_desc = ""
        extensions = []
        if result == wx.ID_OK:
            get_name = ProjectFileSystem.remove_disallowed_filename_chars(dlg.game_name.GetValue())
            get_title = dlg.game_title.GetValue()
            get_author = dlg.author.GetValue()
            get_email = dlg.email.GetValue()
            get_htmldesc = dlg.htmldesc.GetValue()
            get_desc = dlg.desc.GetValue()
            if dlg.lite.GetValue():
                get_library.append("../extensions/adv3Lite/adv3Lite")
            if dlg.liter.GetValue():
                get_library.append("../extensions/adv3Lite/adv3Liter")
            if dlg.custom.GetValue():
                get_library.append("../extensions/adv3Lite/adv3Liter")
                get_library.append(get_name + '_custom')
                extensions = dlg.extensions.GetCheckedStrings()
        dlg.Destroy()
        if get_name != "":

            # we have a new project, let's build a directory for it
            self.notebook.close_all()
            self.project.title = get_title
            self.project.name = get_name
            self.project.author = get_author
            self.project.libraries = get_library
            self.project.email = get_email
            self.project.desc = get_desc.replace('\n', '')
            self.project.htmldesc = get_htmldesc.replace('\n', '')
            ProjectFileSystem.new_project(self.project)
            if extensions:
                self.project.write_library(extensions)
            self.notebook.load_page(self.project.path, "start.t")
            self.object_browser.rebuild_object_catalog()
            self.project_browser.update_files()

            # load classes data from tads project directory
            self.notebook.load_classes(self.project)
            self.Title = "TadsPad - " + self.project.name
            self.menus(True)

    def spell_check(self, event):

        # spell check system through atd web service
        self.notebook.spellcheck(self.project)

    def load_transcript_view(self, event):

        # load transcript viewer with commands from last play-through
        transcript_viewer = TranscriptView.TranscriptViewWindow(self.project, self.preferences["terp"],
                                                                self.preferences["tadspath"],
                                                                self.preferences["terminal"])
        transcript_viewer.Show()

    def preferences_window(self, event):

        # load preferences window
        prefs_window = PrefsEditWindow.PrefsEditWindow(self.preferences)
        prefs_window.Show()

# run main window (top)
app = wx.App(redirect=True)
top = MainWindow("TadsPad")
top.Show()
top.Maximize(True)   # full screen!!!
app.MainLoop()
