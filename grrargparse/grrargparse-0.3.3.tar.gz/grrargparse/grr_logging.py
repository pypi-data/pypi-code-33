import os
import datetime
import sys
import time
import subprocess
import struct
import shlex
import platform
import random

#globals
global log_file,debug,print_level,print_fail_only,base_dir
debug = False
print_level = False
print_fail_only = False
base_dir = os.getcwd()
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'
# end globals


class bcolours:
    BBLUE = '\033[96m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    SPECTRUM = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']

class Logger(object):

    TITLE = 0
    ERROR = 1
    INFO = 2
    DEBUG = 3
    WARNING = 4
    FATAL = 5
    COMMAND = 6

    to_log = True


class UpdatePrinter(object):
    def __init__(self, total=None):
        self.numP = 1
        self.type = type
        self.total = total


    def update(self):
        if self.total is None:
            self.total = "(unknown)"

        if self.numP>1:
            _cursorup()
        print(str(self.numP)+" of "+str(self.total)+" complete")
        self.numP+=1

    def reset(self):
        self.numP = 1

    def load_bar(self):
        if self.numP > 1:
            _cursorup()
        print("Processed: "+str(self.numP) + _non_specific_loading_bar())
        self.numP += 1


def set_outdir(dir):
    global base_dir
    base_dir = dir


def set_logging(status):
    global to_log
    if isinstance(status,bool):
        to_log = status

def blah():
    print("blah")

def set_debugging(status):
    global debug
    if isinstance(status,bool):
        debug = status

def set_include_level(status):
    global include_level
    if isinstance(status,bool):
        include_level = status

def set_print_fail_only(status):
    global print_fail_only
    if isinstance(status,bool):
        print_fail_only = status



def log(tolog, level=Logger.INFO, to_file=True, prefix="", suffix=""):
    global debug



    tolog = prefix+tolog+suffix

    outstr = ""
    if level == Logger.ERROR:
        outstr = (tolog,"ERROR - "+tolog)[print_level]
        print(bcolours.RED + outstr + bcolours.ENDC)

    if level == Logger.INFO:
        outstr = (tolog,"INFO - "+tolog)[print_level]

        print(outstr)

    if level == Logger.FATAL:
        outstr = (tolog,"FATAL - "+tolog)[print_level]

        print(bcolours.RED + outstr + bcolours.ENDC)
        # if fatal log then exit
        exit(1)

    if level == Logger.TITLE:
        outstr = (tolog,"TITLE - "+tolog)[print_level]

        print(bcolours.PURPLE + bcolours.BOLD + outstr + bcolours.ENDC)

    if level == Logger.WARNING:
        outstr = (tolog,"WARNING - "+tolog)[print_level]

        print(bcolours.YELLOW + outstr + bcolours.ENDC)

    if level == Logger.COMMAND:
        outstr = (tolog,"EXEC - "+tolog)[print_level]

        print(bcolours.BLUE + outstr + bcolours.ENDC)

    if level == Logger.DEBUG and debug:
        outstr = (tolog,"DEBUG - "+tolog)[print_level]

        print("DEBUG:  "+outstr)


    # write results to log file
    st = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if to_file and (level != Logger.DEBUG or debug):


        logfile = create_log_file()
        with open(logfile, "a") as myfile:
            outstr = outstr.encode('utf-8').strip()
            myfile.write(st+" - "+ str(outstr) +"\n")


def log_str(tolog, level=Logger.INFO, prefix="", suffix=""):


    tolog = prefix+tolog+suffix

    outstr = ""
    if level == Logger.ERROR:
        outstr = (tolog,"ERROR - "+tolog)[print_level]
        print(bcolours.RED + outstr + bcolours.ENDC)

    if level == Logger.INFO:
        outstr = (tolog,"INFO - "+tolog)[print_level]

        print(outstr)

    if level == Logger.FATAL:
        outstr = (tolog,"FATAL - "+tolog)[print_level]

        return (bcolours.RED + outstr + bcolours.ENDC)

    if level == Logger.TITLE:
        outstr = (tolog,"TITLE - "+tolog)[print_level]

        return (bcolours.PURPLE + bcolours.BOLD + outstr + bcolours.ENDC)

    if level == Logger.WARNING:
        outstr = (tolog,"WARNING - "+tolog)[print_level]

        return (bcolours.YELLOW + outstr + bcolours.ENDC)

    if level == Logger.COMMAND:
        outstr = (tolog,"EXEC - "+tolog)[print_level]

        print(bcolours.BLUE + outstr + bcolours.ENDC)

    if level == Logger.DEBUG and debug:
        outstr = (tolog,"DEBUG - "+tolog)[print_level]

        return (outstr)


def _cursorup():
    sys.stdout.write(CURSOR_UP_ONE)


lastPrint = time.time()
loaddash=""

def _non_specific_loading_bar():
    global loaddash, lastPrint
    now = time.time()
    MAX = 20

    if now-lastPrint>0.1:

        if loaddash == " "*MAX:
            loaddash = ""

        elif loaddash == "*"*MAX:
                loaddash = " "*MAX
        else:
            loaddash += '*'
        lastPrint = now
        return " "+loaddash
    else:
        return ""



def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass


def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])


def _get_terminal_width():
    rows,columns = _get_terminal_size()
    return rows

def _get_terminal_size():

    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        print("default")
        tuple_xy = (80, 25)      # default value
    return tuple_xy



def small_divider():
    print(bcolours.BLUE+"-"*_get_terminal_width()+bcolours.ENDC)
    #print bcolours.BLUE+"------XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-------"+bcolours.ENDC
    #print bcolours.BLUE+"-"*_get_terminal_width()+bcolours.ENDC

def small_divider_str():
    return bcolours.BLUE+"-"*_get_terminal_width()+bcolours.ENDC
    #print bcolours.BLUE+"------XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-------"+bcolours.ENDC
    #print bcolours.BLUE+"-"*_get_terminal_width()+bcolours.ENDC



class SplashScreen(object):
    def __init__(self, banner_array):
        self.banner = banner_array


    def windowprint(self):
        cursor_off()
        ticks = 0
    #    while ticks <= len(banner[0]):
    #        i=0
    #        for l in banner:
    #            bitofstring = " "*(ticks+i)+l[ticks+i:ticks+i+60]
    #            new_str = randomColourString(bitofstring)
    #            sys.stdout.write("%s" %new_str)
    #            sys.stdout.flush()
    #            i-=2
    #            print
    #        time.sleep(0.005)
    #        sys.stdout.write((CURSOR_UP_ONE+ERASE_LINE)*len(banner[0]))
    #        ticks+=1

        for i in range (0,1):
            _banner = []
            columns = _get_terminal_width()
            for l in self.banner:
                c = columns if columns <= len(l) else len(l)
                _banner.append(l[0:c])
            for l in self.banner:
                ll = randomColourString(l)
                sys.stdout.write("%s\n" %ll)
                time.sleep(0.05)
    #        for l in banner:
    #            sys.stdout.write((CURSOR_UP_ONE+ERASE_LINE))
    #            sys.stdout.flush()
    #            time.sleep(0.05)
        print()
        cursor_on()


def randomColourString(in_str):
    nn = list(in_str)
    out_str = ""
    for i in range(0,len(nn),5):
        out_str += random.choice(bcolours.SPECTRUM)+''.join(nn[i:i+5])+bcolours.ENDC
    return out_str


def cursor_on():
    os.system('setterm -cursor on')

def cursor_off():
    os.system('setterm -cursor off')



def divider():
    rows, columns = os.popen('stty size', 'r').read().split()
    print("-"*int(columns))
    print("/"*int(columns))
    print("-"*int(columns))


def divider_str():
    rows, columns = os.popen('stty size', 'r').read().split()
    out = "-"*int(columns)
    out +="/"*int(columns)
    out+="-"*int(columns)
    return out


def set_logging(status):
    if isinstance(status,bool):
        to_log = status



def create_log_file():
    log_file_dir = os.path.join(os.path.expanduser("~"), ".grrargparse")
    # create the dir if it doesn't exist
    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)

    return os.path.join(log_file_dir,"grrarrparse.log")

