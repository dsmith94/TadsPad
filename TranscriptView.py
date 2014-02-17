
#
#   Transcript Display View Window, to show (and play commands) in current game
#

import wx
import os
import BuildProcess


class TranscriptViewWindow(wx.Frame):
    def __init__(self, project, terp, tads3path):
        wx.Frame.__init__(self, None, title="Transcript of Last Session")

        r = wx.Display().GetGeometry()
        self.SetSize(wx.Size(r.Width / 4, r.Height / 2))
        transcript_ctrl = wx.ListCtrl(parent=self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        transcript_ctrl.InsertColumn(0, "Command List", width=r.Width / 4)
        transcript_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.command_activated)
        index = 0
        self.terp = terp
        self.tads3path = tads3path
        self.transcript = process_transcript(project.path)
        self.project = project
        for command in self.transcript:
            transcript_ctrl.InsertStringItem(index, command)
            index += 1
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(transcript_ctrl, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(sizer)
        self.Fit()
        self.Update()

    def command_activated(self, event):

        # command has been activated, fire up 'terp with commands listed
        index_max = event.GetIndex()
        index = 0
        script = ""
        for command in self.transcript:
            script = script + ">" + command + "\n"
            if index == index_max:
                break
            index += 1
        process = BuildProcess.CompileGame
        BuildProcess.run(process, self.project, self.terp, self.tads3path, script)

        self.Close()


def process_transcript(project_path):

    # load a log file from "output.log" and return the transcript for game
    transcript = []
    log_file = open(os.path.join(project_path, "transcript.txt"), 'rU')
    if log_file:
        log_string = log_file.read()
        log_string = log_string.replace("<line>", "")
        if log_string:
            for line in log_string.split('\n'):

                # read output file line by line and extract commands
                if line != "" and line.find(">") < 1:
                    transcript.append(line)

    log_file.close()
    return transcript


__author__ = 'dj'
