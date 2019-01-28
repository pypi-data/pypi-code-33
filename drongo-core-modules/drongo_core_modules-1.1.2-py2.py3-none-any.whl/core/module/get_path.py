import importlib
import os
import six
import sys


if __name__ == '__main__':
    klass = sys.argv[1]
    mod = '.'.join(klass.split('.')[:-1])
    six.print_(os.path.dirname(
        importlib.import_module(mod).__file__
    ), end='')
