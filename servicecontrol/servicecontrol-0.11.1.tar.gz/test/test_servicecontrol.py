from __future__ import print_function
import os
import time
import signal
import sys


def _print(*args, **kwargs):
    print ( *args, **kwargs)
    sys.stdout.flush()

try:
    import prctl
    has_prctl = True
    _print ('has_prctl = True')
except:
    has_prctl = False
    _print ('has_prctl = False')


# from ctypes import cdll
# libc = cdll['libc.so.6']

def sigterm_handler(_signo, _stack_frame):
    _print('PID {}. Got signal {}, but ignoring because I am naughty'.format(os.getpid(), _signo))


for i in range(3):
    pid = os.fork()
    if pid == 0:
        signal.signal(signal.SIGTERM, sigterm_handler)
    my_pid = os.getpid()

    # if os.getpgid(my_pid) != my_pid:
    #     os.setsid()

    if pid != 0:
        _print('{} created a new process {}'.format(os.getpid(), pid))


time.sleep(.2)
# libc.prctl(1, signal.SIGTERM)#signal.SIGKILL)
if has_prctl:
    deathsig = prctl.get_pdeathsig()
else:
    deathsig = 'UNKNOWN'

_print('My PID={}, My PGPID = {}, MySID = {}, My PR_DEATHSIG={}'.format(my_pid, os.getpgid(my_pid), os.getsid(my_pid), deathsig))


for i in range(30):
    try:
        time.sleep(1.0)
    except Exception as e:
        print('Exception {}: {}'.format(e.__class__.__name__, e))

_print("{} Exiting".format(my_pid))

