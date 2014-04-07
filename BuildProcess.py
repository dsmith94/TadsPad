
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

def win32run(the_thread, the_project, compiler, interpreter, script="", flags=""):

    # run if on win32 system
    # compile game for playing
    project_to_compile = flags + " -f \"" + the_project.path + "/" + the_project.filename + "\""
    compile_process = subprocess.Popen(compiler + project_to_compile, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
    output = compile_process.communicate()[0]
    exit_code = compile_process.returncode

    # prepare to play game - get transcript ready
    options = " -o \"" + os.path.join(the_project.path, "transcript.txt\" ")
    if script != "":
        with open(os.path.join(the_project.path, "input.txt"), mode='w') as input_file:
            input_file.write(script)
        options = options + "-i \"" + os.path.join(the_project.path, "input.txt\" ")

    # play if compile was a success
    if exit_code == 0:
        wx.CallAfter(MessageSystem.show_message, "Compile complete")
        playgame = subprocess.Popen(interpreter + options + "\"" + os.path.join(the_project.path, the_project.name + ".t3")
                     + "\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        wx.CallAfter(MessageSystem.show_errors, output)


def nixrun(the_thread, the_project, compiler, interpreter, script="", flags="", terminal="x-terminal-emulator"):

    # run if on unix style system
    # compile game for playing
    project_to_compile = flags + " -f \"" + the_project.path + "/" + the_project.filename + "\""
    compile_process = subprocess.Popen(compiler + project_to_compile, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
    output = compile_process.communicate()[0]
    exit_code = compile_process.returncode

    # prepare to play game - get transcript ready
    input_path = os.path.join(the_project.path, 'input.txt')
    with open(input_path, mode='w') as input_file:
        input_file.write('\n'.join(['>record on', '>transcript.txt\n']))
        if script != "":
            input_file.write(script)

    # play if compile was a success
    if exit_code == 0:
        wx.CallAfter(MessageSystem.show_message, "Compile complete")
        path = os.path.join(the_project.path, the_project.name + ".t3")
        playgame = subprocess.Popen([terminal, '-e', interpreter, '-R', input_path, path], shell=False)
    else:
        wx.CallAfter(MessageSystem.show_errors, output)


def run(the_thread, the_project, terp, tads3path, script="", flags="", terminal=""):

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
    if sys.platform == "win32":
        win32run(the_thread, the_project, compiler, interpreter, script, flags)
    else:
        nixrun(the_thread, the_project, compiler, interpreter, terminal=terminal, script=script, flags=flags)


__author__ = 'dj'
