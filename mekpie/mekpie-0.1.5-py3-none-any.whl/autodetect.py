from os     import name
from shutil import which

import mekpie.messages as messages

from .util        import panic, log, errprint
from .definitions import CC_CMDS

warned = False

def autodetect_compiler():
    global warned
    for cmd in CC_CMDS.keys():
        if defined(cmd):
            return CC_CMDS[cmd]
    if not warned:
        errprint(messages.failed_autodetect + '\n')
        warned = True
    return CC_CMDS['default']

def defined(name):
    return which(name) is not None