
# class making up thread to build tads game when we're done writing it

from threading import Thread
import subprocess
import MessageSystem
import sys
import os
import wx


class CompileGame(Thread):

    def __init__(self):
        Thread.__init__(self)


def run(the_thread, the_project, terp, tads3path, script="", flags=""):

    # compile game for playing
    MessageSystem.clear_errors()
    MessageSystem.show_message("Building " + the_project.name + "...")
    the_project.write()
    if " " in tads3path:
        compiler = "\"" + tads3path + "\""
    else:
        compiler = tads3path
    if " " in terp:
        interpreter = "\"" + terp + "\""
    else:
        interpreter = terp
    project_to_compile = flags + " -f \"" + the_project.path + "/" + the_project.filename + "\""
    """
    if os.path.exists(compiler.replace("\"", "")) is False:
        MessageSystem.error("Could not compile project: " + the_project.filename + ", executable " +
                            compiler + " does not exist.", "Compile failure")
        return
    if os.path.exists(terp.replace("\"", "")) is False:
        MessageSystem.error("Could not compile project: " + the_project.filename + ", executable " +
                            terp + " does not exist.", "Interpreter failure")
        return
    """
    compile_process = subprocess.Popen(compiler + project_to_compile, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
    output = compile_process.communicate()[0]
    exit_code = compile_process.returncode
    options = " "
    if sys.platform == "win32":
        options = " -o \"" + os.path.join(the_project.path, "transcript.txt\" ")
    if script != "":
        input_file = open(os.path.join(the_project.path, "input.txt"), mode='w')
        input_file.write(script)
        input_file.close()
        if sys.platform == "win32":
            options = options + "-i \"" + os.path.join(the_project.path, "input.txt\" ")
    if exit_code == 0:
        wx.CallAfter(MessageSystem.show_message, "Compile complete")
        playgame = subprocess.Popen(interpreter + options + "\"" + os.path.join(the_project.path, the_project.name + ".t3")
                     + "\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        wx.CallAfter(MessageSystem.show_errors, output)


__author__ = 'dj'
