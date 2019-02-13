import sys
sys.path.append('/home/mi/marscher/software/pycharm-2017.2/debug-eggs/pycharm-debug-py3k.egg')

import pydevd

pydevd.settrace('localhost', port=35352, stdoutToServer=True, stderrToServer=True)
