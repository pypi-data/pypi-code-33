'''
system defines an sane api for running executbales.
'''

import os 
import sys 
import shlex
import shutil
import subprocess

# PRIVATE
class _ExecResult:
    '''_ExecResult is a wrapper for the results of subprocess.Popen'''
    def __init__(self, status=None, out=None, err=None, fail=None):
        self.status = status
        try:
            self.out = out.decode('utf8')
        except:
            self.out = None
        try:
            self.err = err.decode('utf8')
        except:
            self.out = None
        self.fail = fail
    def check_ok(self):
        return self.fail == None and self.status == 0 
    def check_output(self):
        return bool(self.out) or bool(self.err)

# INTERFACE
def cd(path):
    '''cd will change the current working directory for the system.exec and system.shell commands'''
    return os.chdir(path)

def exec(cmd):
    '''shell runs executables that DONT need a TUI'''
    parsed = shlex.split(cmd)
    parsed[0] = shutil.which(parsed[0])
    if not parsed[0]:
       return _ExecResult(fail=True) 
    p = subprocess.Popen(parsed, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    status = p.returncode
    return _ExecResult(status, out, err)

def shell(cmd):
    '''shell runs executables that need a TUI'''
    parsed = shlex.split(cmd)
    parsed[0] = shutil.which(parsed[0])
    if not parsed[0]:
       return _ExecResult(fail=True) 
    status = subprocess.Popen(parsed).wait()
    return _ExecResult(status, None, None)

def fail():
    return exec('false')

def success():
    return exec('true')

def check_is_tty():
    return sys.stdout.isatty()

def which(*args):
    return shutil.which(*args)
