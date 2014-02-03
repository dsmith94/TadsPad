
#
#   library to handle tads project files (aka makefiles)
#

import os
import wx
import re
import MessageSystem
import unicodedata
import string
import hashlib
import shutil
from binascii import hexlify


class TadsProject():
    def __init__(self):
        ## init the standard tads project for our subsystems
        self.name = ""
        self.title = ""
        self.author = ""
        self.filename = ""
        self.htmldesc = ""
        self.desc = ""
        self.email = ""
        self.path = ""
        self.files = []
        self.files.append("start.t")


def remove_disallowed_filename_chars(filename):
    valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleaned_filename if c in valid_filename_chars)


class NewProjectWindow(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, title="New Project...")
        screen_geometry = wx.Display().GetGeometry()
        width = screen_geometry.Width / 5
        box_master = wx.BoxSizer(wx.VERTICAL)
        box_for_text = wx.BoxSizer(wx.VERTICAL)
        box_for_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.game_name = wx.TextCtrl(self, size=(width, -1))
        self.game_title = wx.TextCtrl(self, size=(width, -1))
        self.author = wx.TextCtrl(self, size=(width, -1))
        lbl_game_name = wx.StaticText(self, label="New Project Name   ")
        lbl_game_title = wx.StaticText(self, label="Game Title   ")
        lbl_author = wx.StaticText(self, label="Author   ")
        box_for_text.Add(lbl_game_name)
        box_for_text.Add(self.game_name)
        box_for_text.Add(lbl_game_title)
        box_for_text.Add(self.game_title)
        box_for_text.Add(lbl_author)
        box_for_text.Add(self.author)
        ok_button = wx.Button(self, wx.ID_OK, "&OK")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        box_for_buttons.Add(ok_button, 0)
        box_for_buttons.Add(cancel_button)
        box_master.Add(box_for_text, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.Add(box_for_buttons, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.SetSizeHints(self)
        panel = wx.Panel(self)
        panel.SetSizer(box_master)
        panel.Layout()


def get_project_root():

    # get root directory for project folder
    # check first that the folder exists
    path_string = os.path.expanduser('~/Documents/TADS 3/')
    if os.path.exists(path_string) is False:

        # make it if it doesn't exist
        os.makedirs(path_string)

    return path_string


def load_project(file_name, the_project):

    # load project from filename
    try:
        f = open(file_name, 'r')
        file_text = f.read()

        # describe to parser what a source definition looks like
        sources = re.compile("-source ([\s|\"*|a-zA-Z]*)")

        # now get list of sources
        the_project.files[:] = []
        list_of_sources = sources.findall(file_text)
        for source_file in list_of_sources:
            the_project.files.append(source_file.strip('\n').strip('"').strip("'") + ".t")
        f.close()
        the_project.filename = os.path.basename(file_name)
        the_project.name = os.path.splitext(the_project.filename)[0]
        the_project.path = os.path.dirname(file_name)

    except IOError, e:
        MessageSystem.error("Could not load file: " + e.filename + " - fail.", "Project load error")


def generate_ifid(author_and_title_string):
    s = str(hexlify(hashlib.md5(author_and_title_string).digest()).upper())
    s = s[:20] + '-' + s[20:]
    s = s[:16] + '-' + s[16:]
    s = s[:12] + '-' + s[12:]
    s = s[:8] + '-' + s[8:]
    return s


def write_makefile(name_of_project, list_of_files):

    # write makefile, for compilation process
    path_string = get_project_root() + name_of_project + "/"
    try:
        f = open("./makefile.tmp", 'r')
        file_text = f.read()
        file_text = file_text.replace('$NAME$', name_of_project)
        files = ""
        for file_name in list_of_files:
            files = files + "-source " + file_name[:-2] + "\n"
        file_text = file_text.replace('$SOURCE$', files)
        finished = open(path_string + name_of_project + ".t3m", 'w')
        finished.write("%s" % file_text)
        f.close()
        finished.close()
    except IOError, er:
        MessageSystem.error("Could not write data to file. Error:" + er.filename,
                            "Failed to create makefile")


def new_project(name_of_project, the_project):

    # create new project
    path_string = get_project_root()
    os.makedirs(os.path.join(path_string, name_of_project))
    os.makedirs(os.path.join(path_string, name_of_project, "obj"))
    path_string = os.path.join(path_string, name_of_project)
    write_makefile(name_of_project, the_project.files)
    the_project.name = name_of_project
    the_project.filename = name_of_project + ".t3m"
    the_project.path = path_string
    shutil.copyfile("ignore.tmp", os.path.join(path_string, "ignore.txt"))
    try:
        start_tmp = open("./start.tmp", 'r')
        start_tmp_text = start_tmp.read()
        start_tmp.close()
        start_tmp_text = start_tmp_text.replace('$TITLE$', the_project.title)
        start_tmp_text = start_tmp_text.replace('$AUTHOR$', the_project.author)
        start_tmp_text = start_tmp_text.replace('$IFID$', generate_ifid(the_project.author + the_project.title))
        start_tmp_text = start_tmp_text.replace('$DESC$', the_project.desc)
        start_tmp_text = start_tmp_text.replace('$FILENAME$', 'start.t')
        start_tmp_text = start_tmp_text.replace('$HTMLDESC$', the_project.htmldesc)
        start_tmp_text = start_tmp_text.replace('$EMAIL$', the_project.email)
        start_t = open(path_string + "/start.t", 'w')
        start_t.write(start_tmp_text)
        start_t.close()

    except IOError, e:
        MessageSystem.error("Could not retrieve data from file: start.tmp. Error:" + e.filename,
                            "Failed to create project")


__author__ = 'dj'
