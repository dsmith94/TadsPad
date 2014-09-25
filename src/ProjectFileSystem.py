
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
import embedded
import codecs
from binascii import hexlify


class TadsProject():
    def __init__(self):
        ## init the standard tads project for our subsystems
        self.data = ""
        self.name = ""
        self.title = ""
        self.author = ""
        self.filename = ""
        self.htmldesc = ""
        self.desc = ""
        self.email = ""
        self.path = ""
        self.libraries = []
        self.files = []
        self.files.append("start.t")
        self.web = False
        self.phrases = []   # special tags used in making new project files

    def write(self):

        """
        write makefile, for compilation process
        """

        # fix libraries, if using web then specify so
        lib_buffer = []
        for library in self.libraries:
            if library == "../extensions/adv3Lite/adv3Lite" or library == "../extensions/adv3Lite/adv3Liter":
                if library == "../extensions/adv3Lite/adv3Lite":
                    if self.web:
                        lib_buffer.append("../extensions/adv3Lite/adv3LiteWeb")
                    else:
                        lib_buffer.append("../extensions/adv3Lite/adv3Lite")
                else:
                    if self.web:
                        lib_buffer.append("../extensions/adv3Lite/adv3LiterWeb")
                    else:
                        lib_buffer.append("../extensions/adv3Lite/adv3Liter")
            else:
                lib_buffer.append(library)
        if self.web:
            if "webui" not in lib_buffer:
                lib_buffer.append("webui")
        self.libraries = lib_buffer

        # proceed with makefile
        path_string = os.path.join(get_project_root(), self.name)
        text = self.data
        text = text.replace('$NAME$', self.name)
        files = "\n-source "
        files += "\n-source ".join([f[:-2] for f in self.files])
        text = text.replace('$SOURCE$', files)
        libraries = "\n-lib "
        libraries += "\n-lib ".join(self.libraries)
        text = text.replace('$LIBRARY$', libraries)
        try:
            with open(os.path.join(path_string, self.name + ".t3m"), 'w') as finished:
                finished.write(text)
        except IOError, er:
            MessageSystem.error("Could not write data to file. Error:" + er.filename,
                                "Failed to create makefile")

    def write_library(self, sources):

        # write a custom library from a list source code files
        sources = map(lambda x: 'source: ' + x.replace("\\", "/"),
                      [os.path.join(get_project_root(), 'extensions', 'adv3Lite', s) for s in sources])
        code = "name: " + self.name + " custom Library\n" + '\n'.join(sources)
        path = os.path.join(get_project_root(), self.name, self.name + '_custom.tl')
        try:
            with open(path, 'w') as f:
                f.write(code)
        except IOError as e:
            MessageSystem.error("Could not write custom library for " + self.name,
                                "Error writing library file " + e.filename)

    def new_file(self, template, dest):

        # create a new file for project, with tokens changed to match current project config
        # use tokens from phrases string
        text = template
        for old, new in self.phrases:
            text = text.replace(old, new)
        text = text.replace("$FILENAME$", dest)
        text = text.replace("$TITLE$", self.name)
        try:
            with codecs.open(os.path.join(self.path, dest), 'w', "utf-8") as f:
                f.write(text)
        except IOError, e:
            MessageSystem.error("Could not write file: " + e.filename, "File Write Failure")


def remove_disallowed_filename_chars(filename):
    valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleaned_filename if c in valid_filename_chars)


class NewProjectWindow(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, title="New Project...")

        # get extensions
        path = os.path.join(get_project_root(), "extensions", "adv3Lite")
        filetree = os.walk(path, True)
        extensions = get_differences_lite()
        for root, dirs, files in filetree:
            for d in dirs:

                # skip template and docs
                if d != "template" and d != "docs":
                    subpath = os.walk(os.path.join(path, d), True)
                    for subroot, subdir, subfiles in subpath:
                        for f in subfiles:
                            if f[-2:] == '.t':
                                extensions.append(os.path.join(d, f[:-2]))

        # build ui
        screen_geometry = wx.Display().GetGeometry()
        width = screen_geometry.Width / 5
        box_master = wx.BoxSizer(wx.VERTICAL)
        box_for_text = wx.BoxSizer(wx.VERTICAL)
        box_for_buttons = wx.BoxSizer(wx.HORIZONTAL)
        box_for_custom = wx.BoxSizer(wx.VERTICAL)
        box_for_split = wx.BoxSizer(wx.HORIZONTAL)
        box_for_desc = wx.BoxSizer(wx.VERTICAL)
        self.game_name = wx.TextCtrl(self, size=(width, -1))
        self.game_name.Bind(wx.EVT_TEXT, self.determine_ok)
        self.game_title = wx.TextCtrl(self, size=(width, -1))
        self.author = wx.TextCtrl(self, size=(width, -1))
        lbl_game_name = wx.StaticText(self, label="New Project Name   ")
        lbl_game_title = wx.StaticText(self, label="Game Title   ")
        lbl_author = wx.StaticText(self, label="Author   ")
        lbl_email = wx.StaticText(self, label="Email   ")
        self.email = wx.TextCtrl(self, size=(width, -1))
        self.email.Value = "author@email.com"
        self.htmldesc = wx.TextCtrl(self, size=(width, -1), style=wx.TE_MULTILINE)
        self.htmldesc.Value = "Write game description here (html tags accepted)..."
        self.htmldesc.Bind(wx.EVT_TEXT, lambda x: self.desc.SetValue(convert_html(self.htmldesc.Value)))
        self.desc = wx.TextCtrl(self, size=(width, -1), style=wx.TE_MULTILINE)
        self.desc.Value = "Write game description here..."
        self.lite = wx.RadioButton(self, -1, 'adv3Lite', style=wx.RB_GROUP)
        self.lite.Bind(wx.EVT_RADIOBUTTON, self.custom_checked, id=wx.ID_ANY)
        self.liter = wx.RadioButton(self, -1, 'adv3Liter')
        self.liter.Bind(wx.EVT_RADIOBUTTON, self.custom_checked, id=wx.ID_ANY)
        self.custom = wx.RadioButton(self, -1, 'Custom')
        self.custom.Bind(wx.EVT_RADIOBUTTON, self.custom_checked, id=wx.ID_ANY)
        self.web = wx.CheckBox(self, -1, 'Web Play')
        self.extensions = wx.CheckListBox(self, id=-1, choices=extensions)
        self.extensions.Enabled = False
        box_for_custom.Add(self.custom)
        box_for_custom.Add(self.extensions)
        box_for_text.Add(lbl_game_name)
        box_for_text.Add(self.game_name)
        box_for_text.Add(lbl_game_title)
        box_for_text.Add(self.game_title)
        box_for_text.Add(lbl_author)
        box_for_text.Add(self.author)
        box_for_text.Add(lbl_email)
        box_for_text.Add(self.email)
        box_for_text.Add(wx.StaticText(self, label="Choose Library:    "))
        box_for_text.Add(self.lite)
        box_for_text.Add(self.liter)
        box_for_text.Add(box_for_custom)
        box_for_text.Add(self.web)
        self.ok_button = wx.Button(self, wx.ID_OK, "&OK")
        self.ok_button.Enabled = False
        cancel_button = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        box_for_buttons.Add(self.ok_button, 0)
        box_for_buttons.Add(cancel_button)
        box_for_desc.Add(wx.StaticText(self, label="Game Description (in HTML):    "))
        box_for_desc.Add(self.htmldesc, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_for_desc.Add(wx.StaticText(self, label="Game Description (non HTML):    "))
        box_for_desc.Add(self.desc, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_for_split.Add(box_for_text)
        box_for_split.Add(box_for_desc, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.Add(box_for_split, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.Add(box_for_buttons, 0, wx.EXPAND | wx.ALL, border=width / 10)
        box_master.SetSizeHints(self)
        box_master.Layout()
        self.SetSizer(box_master)
        self.Fit()
        self.Update()

    def determine_ok(self, event):

        # determine whether the ok button should be grayed/ungrayed
        if self.game_name.Value == '':
            self.ok_button.Enabled = False
        else:
            self.ok_button.Enabled = True

    def custom_checked(self, event):

        # when custom checkbox is clicked, ungray (or gray) extensions box
        self.extensions.Enabled = self.custom.GetValue()

        # if the extensions are enabled, everything not in adv3lite is checked by default
        if self.extensions.Enabled:
            for index, text in enumerate(self.extensions.GetStrings()):
                if '/' not in text:
                    self.extensions.Check(index)


def get_project_root():

    # get root directory for project folder
    # check first that the folder exists
    if os.path.exists(os.path.expanduser("~/documents")):
        path = os.path.join(os.path.expanduser("~/documents"), 'TADS 3')
    else:
        path = os.path.join(os.path.expanduser("~/Documents"), 'TADS 3')

    if os.path.exists(path) is False:

        # make it if it doesn't exist
        os.makedirs(path)

    return path


def generate_ifid(author_and_title_string):
    s = str(hexlify(hashlib.md5(author_and_title_string).digest()).upper())
    s = s[:20] + '-' + s[20:]
    s = s[:16] + '-' + s[16:]
    s = s[:12] + '-' + s[12:]
    s = s[:8] + '-' + s[8:]
    return s


def get_differences_lite():

    # return in a list the differences between adv3Lite and adv3Liter
    # we could just hard code this, but having the ide figure it out future-proofs this

    # open both libraries
    adv3Lite = None
    adv3Liter = None
    path = os.path.join(get_project_root(), 'extensions', 'adv3Lite')
    with open(os.path.join(path, 'adv3Lite.tl')) as f:
        adv3Lite = [line for line in f]
    with open(os.path.join(path, 'adv3Liter.tl')) as f:
        adv3Liter = [line for line in f]

    # check differences source files in both libraries now that we have them
    # return list
    if adv3Lite is not None:
        if adv3Liter is not None:
            return [s.replace('source: ', '').strip() for s in adv3Lite if s not in adv3Liter if 'source: ' in s]
    return None


def load_project(file_name):

    """
    Analyze project file at file name, build it into memory
    """

    # load project from filename
    the_project = TadsProject()
    try:
        with open(file_name, 'rU') as f:
            file_text = f.read()
    except IOError, e:
        MessageSystem.error("Could not load file: " + e.filename + " - fail.", "Project load error")
        return None
    else:

        # describe to parser what the source definition looks like
        sources = re.compile("-source ([\s|\"*|a-zA-Z]*)")
        library = re.compile("-lib (.*)\n")

        # determine if it is a webgame
        if "-D TADS_INCLUDE_NET" in file_text:

            # we have a webgame!
            the_project.web = True

        # get libraries used
        match = library.findall(file_text)
        if match:

            # found libraries, use them
            the_project.libraries = match

        # now get list of sources
        the_project.files[:] = []
        start = file_text.find('\n##sources')
        list_of_sources = sources.findall(file_text[start:])
        the_project.files = [s.strip('\n').strip('"').strip("'") + ".t" for s in list_of_sources if s if s != 'tadsnet']

        # now rewrite the sources part of the file in case we make any changes
        the_project.data = file_text[:start] + '\n$LIBRARY$\n\n##sources $SOURCE$\n'

        # remove the libraries from the source data
        the_project.data = library.sub("", the_project.data)

        # and get ready to replace the name when we need to
        the_project.data = re.sub("-o (.*).t3\n", "-o $NAME$.t3\n", the_project.data)

        # finish project setup - get name and path
        the_project.filename = os.path.basename(file_name)
        the_project.name = os.path.splitext(the_project.filename)[0]
        the_project.path = os.path.dirname(file_name)
        return the_project


def convert_html(s):

    # basic convert html to plain text
    skip = False
    text = ""
    for c in s:
        if c == '<':
            skip = True
        if c == '&':
            skip = True
        if not skip:
            text += c
        if c == '>':
            skip = False
        if c == ';':
            skip = False

    return text


def new_project(the_project):

    # create new project
    path_string = get_project_root()
    os.makedirs(os.path.join(path_string, the_project.name))
    os.makedirs(os.path.join(path_string, the_project.name, "obj"))
    path_string = os.path.join(path_string, the_project.name)
    if the_project.web:
        the_project.data = embedded.web_makefile
    else:
        the_project.data = embedded.makefile
    the_project.write()
    the_project.filename = the_project.name + ".t3m"
    the_project.path = path_string
    the_project.phrases = (('$AUTHOR$', the_project.author),
                          ('$IFID$', generate_ifid(the_project.author + the_project.title)),
                          ('$DESC$', convert_html(the_project.htmldesc)), ('$HTMLDESC$', the_project.htmldesc),
                          ('$EMAIL$', the_project.email))
    the_project.new_file(embedded.start, 'start.t')
    the_project.new_file(embedded.ignore, "ignore.txt")


__author__ = 'dj'