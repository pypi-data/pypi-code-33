import os
import sys
import cmd
import glob
from .grr_logging import log
from .grr_logging import Logger
from .grr_logging import bcolours
from .grr_logging import cursor_on


import signal
import atexit
import shelve
from shelve import Shelf

# Global Persistence store
store = None

def capture_text( question, default=None):
    if default is not None:
        d = "Use default: ["+str(default)+"]?"
        if query_yes_no(d, default="No"):
            print("Using default: " + default)
            return default

    t = input(question+": ")
    return t


def query_yes_no(question, default="yes"):
    default = default.lower()


    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def j(*args):
    return os.path.join(*args)


def do_final():
    cursor_on()
    close_store()


def signal_handler(a,b):
    log('\n\nExiting (by SIGINT - bye !\n', Logger.FATAL)


def exit_handler():
    atexit.register(do_final)
    signal.signal(signal.SIGINT, signal_handler)


def _append_slash_if_dir(p):
    if p and os.path.isdir(p) and p[-1] != os.sep:
        return p + os.sep
    else:
        return p


def get_persistence_store():
    global store
    if store is not None:
        return store
    else:
        return shelve.open("./.grrargparse_state",writeback=True)





def close_store():
    global store
    if store is not None:
        store.close()

def flush_store():
    store = get_persistence_store()
    store.clear()



def capture_file( default=None, must_exist=False, must_not_exist=False, must_be_file=False, must_be_folder=False):
    dir = os.curdir

    if default is not None and default != "None":
        dd = os.path.abspath(default)
        d = "Use default: ["+str(dd)+"]?"
        if query_yes_no(d, default="Yes"):
            print("Using default: " + dd)
            return dd

    a = MyShell()
    if must_exist:
        a.must_exist()
    if must_not_exist:
        a.must_not_exist()
    if must_be_file:
        a.must_be_file()
    if must_be_folder:
        a.must_be_folder()
    a.cmdloop( bcolours.GREEN+"load <filename> | ls <dir> | cd <dir> | help"+bcolours.ENDC   )
    return a.get_file()



class MyShell(cmd.Cmd):
    prompt = bcolours.GREEN+"[Choose file] "+os.getcwd()+"/"+" -> "+bcolours.ENDC
    olddir = os.getcwd()
    m_exist = False
    m_not_exist = False
    m_file = False
    m_folder = False

    def get_file(self):
        return self.f

    def must_exist(self):
        self.m_exist = True

    def must_not_exist(self):
        self.m_not_exist = True

    def must_be_file(self):
        self.m_file = True

    def must_be_folder(self):
        self.m_folder = True

    def do_load(self, line):
        f_name = os.path.abspath(line)
        print("load: "+ f_name)
        if os.path.exists(f_name) and self.m_not_exist:
            log("File / folder already exists: "+f_name,Logger.WARNING)
        elif not os.path.exists(f_name) and self.m_exist:
            log("File / folder does not exist"+f_name,Logger.WARNING)
        elif os.path.isdir(f_name) and self.m_file:
            log("Expecting file and got folder",Logger.WARNING)
        elif os.path.isfile(f_name) and self.m_folder:
            log("Expecting folder and got file",Logger.WARNING)

        else:
            self.f = os.path.abspath(f_name)
            os.chdir(self.olddir)
            return True

    def do_cd(self, line):
        if os.path.isdir(line):
            os.chdir(line)
        else:
            log("Not a valid directory",Logger.WARNING)
        self.prompt =  bcolours.GREEN+"[Choose file] "+os.getcwd()+"/"+" -> "+bcolours.ENDC

    def do_ls(self, line):
        if os.path.exists(os.path.abspath(line)):
            print("Directory listing of "+ os.path.abspath(line))
            if line == "" or line is None:
                tolist=os.getcwd()
            else:
                tolist=os.path.abspath(line)

            for l in os.listdir(tolist):
                print("\t"+l)

    def complete_load(self, text, line, begidx, endidx):
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return # arg not found

        fixed = line[before_arg+1:begidx]  # fixed portion of the arg
        arg = line[before_arg+1:endidx]
        pattern = arg + '*'

        completions = []
        for path in glob.glob(pattern):
            path = _append_slash_if_dir(path)
            completions.append(path.replace(fixed, "", 1))
        return completions

    def complete_cd(self, text, line, begidx, endidx):
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return # arg not found

        fixed = line[before_arg+1:begidx]  # fixed portion of the arg
        arg = line[before_arg+1:endidx]
        pattern = arg + '*'

        completions = []
        for path in glob.glob(pattern):
            path = _append_slash_if_dir(path)
            completions.append(path.replace(fixed, "", 1))
        return completions

    def complete_ls(self, text, line, begidx, endidx):
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return # arg not found

        fixed = line[before_arg+1:begidx]  # fixed portion of the arg
        arg = line[before_arg+1:endidx]
        pattern = arg + '*'

        completions = []
        for path in glob.glob(pattern):
            path = _append_slash_if_dir(path)
            completions.append(path.replace(fixed, "", 1))
        return completions


