
# class making up thread to build tads game when we're done writing it

from threading import Thread
import subprocess
import MessageSystem
import ProjectFileSystem
import os
import wx


class CompileGame(Thread):

    def __init__(self):
        Thread.__init__(self)


def run(the_thread, the_project):

    # compile game for playing
    MessageSystem.show_message("Building " + the_project.name + "...")
    ProjectFileSystem.write_makefile(the_project.name, the_project.files)
    tads3path = "\"C:/Program Files/TADS 3/t3make.exe\" "
    options = " -o \"" + os.path.join(the_project.path, "transcript.txt\" ")
    interpreter = "\"C:/Program Files/TADS 3/htmlt3.exe\" "
    project_to_compile = "-f \"" + the_project.path + "/" + the_project.filename + "\""
    compile_process = subprocess.Popen(tads3path + project_to_compile, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
    output = compile_process.communicate()[0]
    exit_code = compile_process.returncode
    if exit_code == 0:
        wx.CallAfter(MessageSystem.show_message, "Compile complete")
        wx.CallAfter(subprocess.Popen, interpreter + options + "\"" + os.path.join(the_project.path, the_project.name +
                                                                                   ".t3") + "\"", shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        wx.CallAfter(MessageSystem.show_errors, output)


__author__ = 'dj'
