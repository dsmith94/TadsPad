
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
        self.library = ""
        self.files = []
        self.files.append("start.t")
        self.phrases = []   # special tags used in making new project files

    def write(self):

        # write makefile, for compilation process
        path_string = get_project_root() + self.name + "/"
        try:
            f = open("./makefile.tmp", 'r')
            file_text = f.read()
            file_text = file_text.replace('$NAME$', self.name)
            files = ""
            for file_name in self.files:
                files = files + "-source " + file_name[:-2] + "\n"
            file_text = file_text.replace('$SOURCE$', files)
            file_text = file_text.replace('$LIBRARY$', self.library)
            finished = open(path_string + self.name + ".t3m", 'w')
            finished.write("%s" % file_text)
            f.close()
            finished.close()
        except IOError, er:
            MessageSystem.error("Could not write data to file. Error:" + er.filename,
                                "Failed to create makefile")

    def new_file(self, name, dest):

        # create a new file for project, with tokens changed to match current project config
        # use tokens from phrases string
        try:
            temp_file = open("./" + name + ".tmp", 'rU')
            text = temp_file.read()
            temp_file.close()
        except IOError, e:
            MessageSystem.error("Could not retrieve data from file: " + e.filename,
                                "File Read Failure")
        else:
            for pair in self.phrases:
                text = text.replace(pair[0], pair[1])
            text = text.replace("$FILENAME$", dest)
            text = text.replace("$TITLE$", self.name)
            try:
                final_file = open(os.path.join(self.path, dest), 'w')
                final_file.write(text)
                final_file.close()
            except IOError, e:
                MessageSystem.error("Could not write file: " + e.filename,
                                    "File Write Failure")


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
        self.lite = wx.RadioButton(self, -1, 'adv3Lite', style=wx.RB_GROUP)
        self.liter = wx.RadioButton(self, -1, 'adv3Liter')
        box_for_text.Add(lbl_game_name)
        box_for_text.Add(self.game_name)
        box_for_text.Add(lbl_game_title)
        box_for_text.Add(self.game_title)
        box_for_text.Add(lbl_author)
        box_for_text.Add(self.author)
        box_for_text.Add(self.lite)
        box_for_text.Add(self.liter)
        ok_button = wx.Button(self, wx.ID_OK, "&OK")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        box_for_buttons.Add(ok_button, 0)
        box_for_buttons.Add(cancel_button)
        box_master.Add(box_for_text, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.Add(box_for_buttons, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.SetSizeHints(self)
        box_master.Layout()
        self.SetSizer(box_master)
        self.Fit()
        self.Update()


def get_project_root():

    # get root directory for project folder
    # check first that the folder exists
    path_string = os.path.expanduser('~/Documents/TADS 3/')
    if os.path.exists(path_string) is False:

        # make it if it doesn't exist
        os.makedirs(path_string)

    return path_string


def generate_ifid(author_and_title_string):
    s = str(hexlify(hashlib.md5(author_and_title_string).digest()).upper())
    s = s[:20] + '-' + s[20:]
    s = s[:16] + '-' + s[16:]
    s = s[:12] + '-' + s[12:]
    s = s[:8] + '-' + s[8:]
    return s


def load_project(file_name):

    # load project from filename
    the_project = TadsProject()
    try:
        f = open(file_name, 'r')
        file_text = f.read()
        f.close()
    except IOError, e:
        MessageSystem.error("Could not load file: " + e.filename + " - fail.", "Project load error")
        return None
    else:

        # describe to parser what a source definition looks like
        sources = re.compile("-source ([\s|\"*|a-zA-Z]*)")
        library = re.compile("-lib \.\./extensions/adv3Lite/(\w*)")

        # get library used
        match = library.findall(file_text)
        if match:
            # found library, use it
            the_project.library = match[0]
        else:
            # no match found, default is adv3lite
            the_project.library = "adv3Lite"

        # now get list of sources
        the_project.files[:] = []
        list_of_sources = sources.findall(file_text)
        for source_file in list_of_sources:
            the_project.files.append(source_file.strip('\n').strip('"').strip("'") + ".t")
        the_project.filename = os.path.basename(file_name)
        the_project.name = os.path.splitext(the_project.filename)[0]
        the_project.path = os.path.dirname(file_name)
        return the_project


def new_project(the_project):

    # create new project
    path_string = get_project_root()
    os.makedirs(os.path.join(path_string, the_project.name))
    os.makedirs(os.path.join(path_string, the_project.name, "obj"))
    path_string = os.path.join(path_string, the_project.name)
    the_project.write()
    the_project.filename = the_project.name + ".t3m"
    the_project.path = path_string
    the_project.phrases = (('$AUTHOR$', the_project.author), \
                          ('$IFID$', generate_ifid(the_project.author + the_project.title)), \
                          ('$DESC$', the_project.desc), ('$HTMLDESC$', the_project.htmldesc), \
                          ('$EMAIL$', the_project.email))
    the_project.new_file("start", 'start.t')
    the_project.new_file("ignore", "ignore.txt")


__author__ = 'dj'
