#!/usr/bin/python

#
#   Primary source file for TadsPad
#   written by dj
#

import wx
import BuildMainUi
import MessageSystem
import BuildProcess
import ProjectFileSystem
import pickle
import os


class MainWindow(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title)

        # user preferences - blank by default, until we load something in them
        self.preferences = {}

        # build main user interface
        BuildMainUi.init(self)
        self.Bind(wx.EVT_CLOSE, self.on_quit)

        # pass reference to this window to the message subsystem
        MessageSystem.MainWindow.instance = self

        # load last project
        self.project = ProjectFileSystem.TadsProject()
        self.on_load()

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

    def new_page(self, event):

        # add new file to project (and query user for the name of the file)
        dlg = MessageSystem.EntryWindow("Please enter name of new file to add to project:")
        result = dlg.ShowModal()
        if result == wx.ID_OK:

            # clean up name for use as a filename
            new_name = ProjectFileSystem.remove_disallowed_filename_chars(dlg.entry.GetValue())

            # name is valid, so continue
            if new_name != "":
                self.notebook.new_page(new_name, self.project, self.object_browser)
                self.project_browser.update_files()

            # name is not valid, forget it
            else:
                MessageSystem.error("No valid name selected - no new project file added.", "Sorry!")

    def on_load(self):

        # when loading tadspad, check for existence of program preferences
        path = os.path.join(os.getenv('APPDATA'), "tadspad/prefs.conf")
        if os.path.exists(path):

            # it exists! load file so we get prefs from last time
            try:
                the_file = open(path, 'rb')
                self.preferences = pickle.load(the_file)
                the_file.close()
                self.load_preferences()
            except IOError:
                MessageSystem.error("Could not read file: " + path, path + " corrupted")

            return

        # no pref.conf, it's our first time loading tadspad
        self.first_time_load()

    def load_preferences(self):

        # load program preferences from file
        # chief here is the last opened project
        ProjectFileSystem.load_project(self.preferences["last project"], self.project)
        self.object_browser.rebuild_object_catalog()
        self.project_browser.update_files()

    def first_time_load(self):

        # first time loading tadspad, give user some options
        MessageSystem.error("Welcome to TadsPad! Let's make a new project together.", "First time user")
        self.insist_on_new_project()

    def save_preferences(self):

        # save preferences to file before quit
        path = os.getenv('APPDATA') + "/tadspad"
        if not os.path.exists(path):
            os.makedirs(path)
        path += "/prefs.conf"
        self.preferences.update({"last project": os.path.join(self.project.path, self.project.filename)})
        try:
            output = open(path, 'wb')
            pickle.dump(self.preferences, output)
            output.close()
        except IOError, e:
            MessageSystem.error("Could not save preferences: " + e.filename, "File write error")
        ProjectFileSystem.write_makefile(self.project.name, self.project.files)

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

    def play_project(self, event):

        # compile and run current tads story
        # to do this, make a new thread
        process = BuildProcess.CompileGame
        BuildProcess.run(process, self.project)

    def load_project(self, event):

        # load previously worked on project
        path = os.path.abspath(os.path.expanduser("~/Documents/TADS 3/"))
        loadFileDialog = wx.FileDialog(self, "Load .t3m file", "", "", "t files (*.t3m)|*.t3m",
                                       wx.FD_OPEN)
        if loadFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        else:
            ProjectFileSystem.load_project(loadFileDialog.Path, self.project)
            self.project_browser.update_files()
            self.object_browser.rebuild_object_catalog()
            self.notebook.close_all()

    def save_page(self, event):

        # save this page
        self.notebook.save_page(self.object_browser)
        self.project_browser.update_files()

    def save_page_as(self, event):

        # save this page under another filename
        self.notebook.save_page_as(self.object_browser)
        self.project_browser.update_files()

    def save_all(self, event):

        # save all modified files
        self.notebook.save_all(self.object_browser)
        self.project_browser.update_files()

    def insist_on_new_project(self):

        # FORCE the user to make a new project, or quit tadspad
        self.new_project_window(True)

    def new_project(self, event):

        # new project, but don't insist
        self.new_project_window(False)

    def show_message(self, text):

        # display text in message pane
        self.message_pane.show_message(text)

    def show_errors(self, text):

        # display errors text in message pane
        self.message_pane.show_output(text)

    def new_project_window(self, insist_mode):

        # create a new project. if insist mode is on, keep user from NOT making a project

        # call the new project routine from library
        self.project = ProjectFileSystem.TadsProject()
        dlg = ProjectFileSystem.NewProjectWindow()
        result = dlg.ShowModal()
        get_name = ""
        get_title = ""
        get_author = ""
        if result == wx.ID_OK:
            get_name = ProjectFileSystem.remove_disallowed_filename_chars(dlg.game_name.GetValue())
            get_title = dlg.game_title.GetValue()
            get_author = dlg.author.GetValue()
        dlg.Destroy()
        if get_name != "":

            # we have a new project, let's build a directory for it
            self.project.title = get_title
            self.project.author = get_author
            ProjectFileSystem.new_project(get_name, self.project)
            self.notebook.load_page(self.project.path, "start.t", self.project.title, self.object_browser)

        else:
            if insist_mode:
                MessageSystem.error("No project name given, TadsPad will now exit", "Goodbye!!")
                self.Close(0)

        self.project_browser.update_files()



# run main window (top)
app = wx.App(redirect=True)
top = MainWindow("TadsPad")
top.Show()
top.Maximize(True)   # full screen!!!
app.MainLoop()

