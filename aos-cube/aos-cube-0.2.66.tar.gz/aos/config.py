import re
from util import *


# Cfg classed used for handling the config backend
class Cfg(object):
    path = None
    file = ".aos"

    def __init__(self, path):
        self.path = path

    # Sets config value
    def set(self, var, val):
        if not re.match(r'^([\w+-]+)$', var):
            error("%s is invalid config variable name" % var)

        fl = os.path.join(self.path, self.file)
        try:
            with open(fl) as f:
                lines = f.read().splitlines()
        except (IOError, OSError):
            lines = []

        for line in lines:
            m = re.match(r'^([\w+-]+)\=(.*)$', line)
            if m and m.group(1) == var:
                lines.remove(line)

        if not val is None:
            lines += [var + "=" + val]

        try:
            with open(fl, 'w') as f:
                f.write('\n'.join(lines) + '\n')
        except (IOError, OSError):
            warning("Unable to write config file %s" % fl)

    # Gets config value
    def get(self, var, default_val=None):
        fl = os.path.join(self.path, self.file)
        try:
            with open(fl) as f:
                lines = f.read().splitlines()
        except (IOError, OSError):
            lines = []

        for line in lines:
            m = re.match(r'^([\w+-]+)\=(.*)$', line)
            if m and m.group(1) == var:
                return m.group(2)
        return default_val

    # Get all config var/values pairs
    def list(self):
        fl = os.path.join(self.path, self.file)
        try:
            with open(fl) as f:
                lines = f.read().splitlines()
        except (IOError, OSError):
            lines = []

        vars = {}
        for line in lines:
            m = re.match(r'^([\w+-]+)\=(.*)$', line)
            if m and m.group(1) and m.group(1) != 'ROOT':
                vars[m.group(1)] = m.group(2)
        return vars


# Global class used for global config
class Global(object):
    path = os.path.join(os.path.expanduser("~"), '.aos')

    def __init__(self):
        if not os.path.exists(Global.path):
            try:
                os.mkdir(Global.path)
            except (IOError, OSError):
                try:
                    os.mkdir(Global.path)
                except (IOError, OSError):
                    pass

    @staticmethod
    def get_path():
        return Global.path

    @staticmethod
    def get_cfg(*args, **kwargs):
        return Cfg(Global.path).get(*args, **kwargs)

    @staticmethod
    def set_cfg(*args, **kwargs):
        return Cfg(Global.path).set(*args, **kwargs)

    @staticmethod
    def list_cfg(*args, **kwargs):
        return Cfg(Global.path).list(*args, **kwargs)
