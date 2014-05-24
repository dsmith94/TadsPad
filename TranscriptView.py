
#
#   Transcript Display View Window, to show (and play commands) in current game
#

import wx
import os
import BuildProcess
import MessageSystem
import ProjectFileSystem
import codecs


class TranscriptViewWindow(wx.Frame):
    def __init__(self, project, terp, tads3path, terminal):
        wx.Frame.__init__(self, None, title="Transcript of Last Session")

        r = wx.Display().GetGeometry()
        self.SetSize(wx.Size(r.Width / 2, r.Height / 2))
        self.transcript_ctrl = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.transcript_ctrl.InsertColumn(0, "Command List", width=r.Width / 4)
        self.transcript_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.command_activated)
        self.terp = terp
        self.tads3path = tads3path
        self.project = project
        self.terminal = terminal
        path = os.path.join(project.path, "transcript.txt")
        if os.path.exists(path):
            self.transcript = process_transcript(path)
            for i, command in enumerate(self.transcript):
                self.transcript_ctrl.InsertStringItem(i, command)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.transcript_ctrl, 1, wx.EXPAND | wx.ALL)
        button_area = wx.BoxSizer(wx.HORIZONTAL)
        self.load_button = wx.Button(parent=self, label='Load Transcript')
        self.load_button.Bind(wx.EVT_BUTTON, self.load_transcript)
        self.save_button = wx.Button(parent=self, label='Save Transcript')
        self.save_button.Bind(wx.EVT_BUTTON, self.save_transcript)
        button_area.Add(self.load_button, 0, wx.ALL, border=r.Width / 50)
        button_area.Add(self.save_button, 0, wx.ALL, border=r.Width / 50)
        sizer.Add(button_area)
        self.SetSizer(sizer)
        self.Fit()
        self.Maximize()

    def command_activated(self, event):

        # command has been activated, fire up 'terp with commands listed
        index_max = event.GetIndex()
        index = 0
        script = ""
        for command in self.transcript:
            script = script + ">" + command.strip('>') + "\n"
            if index == index_max:
                break
            index += 1
        process = BuildProcess.CompileGame
        BuildProcess.run(process, self.project, self.terp, self.tads3path, script=script, flags=' -v -d ',
                         terminal=self.terminal)
        self.Close()

    def load_transcript(self, event):

        # load transcript from previous saved file
        dialog = wx.FileDialog(self, "Load Transcript from File", "", "", "txt files (*.txt)|*.txt", wx.FD_OPEN)
        dialog.Path = self.project.path + "/"
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        else:
            path = dialog.Path
            if os.path.exists(path):
                self.transcript = process_transcript(path)
                self.transcript_ctrl.DeleteAllItems()
                for i, command in enumerate(self.transcript):
                    self.transcript_ctrl.InsertStringItem(i, command)
                self.Title = "Transcript of " + os.path.basename(path)
            else:
                MessageSystem.error("File not found: " + path, "Cannot Load Transcript")

    def save_transcript(self, event):

        # save transcript file to text
        dialog = wx.FileDialog(self, "Save Transcript", "", "", "txt files (*.txt)|*.txt", wx.FD_SAVE)
        dialog.Path = self.project.path + "/"
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        else:
            path = dialog.Path
            script = u'<eventscript>\n<line>' + u'\n<line>'.join(self.transcript)
            try:
                with codecs.open(path, 'w', "utf-8") as f:
                    f.write(script)
            except IOError:
                MessageSystem.error("Could not write transcript file: " + path, "Transcript Action Failure")

def process_transcript(path):

    # load a log file from  and return the transcript for game
    transcript = []
    try:
        with codecs.open(path, 'rU', "utf-8") as log_file:
            log_string = log_file.read()
            log_string = log_string.replace("<line>", "")
            if log_string:
                for line in log_string.split('\n'):

                    # read output file line by line and extract commands
                    if line != "" and line.find(">") < 1:
                        transcript.append(line)
    except IOError:
        MessageSystem.error("Could not load " + path + ", file corrupted or does not exist." "Transcript Load Failure")
    return transcript


__author__ = 'dj'
