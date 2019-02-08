#!/usr/bin/python3
import json
import logging
import logging.config
import os

from PyQt5 import QtCore, QtDBus

DB_DIR = os.path.expanduser("~/.config/qoob/")
global name; name = "qoob"


def copyDict(dictionnary):
    # from https://writeonly.wordpress.com/2009/05/07/deepcopy-is-a-pig-for-simple-data
    out = dict().fromkeys(dictionnary)
    for key, value in dictionnary.items():
        try:
            out[key] = value.copy()  # dicts, sets
        except AttributeError:
            try:
                out[key] = value[:]  # lists, tuples, strings, unicode
            except TypeError:
                out[key] = value  # ints
    return out


class Database(object):
    def __init__(self, dbFile):
        self.dbFile = DB_DIR + dbFile + ".json"
        if not os.path.isdir(DB_DIR):
            os.mkdir(DB_DIR)
        if os.path.isfile(self.dbFile) and os.stat(self.dbFile).st_size > 0:
            self.load()
        else:
            self.db = {}
            with open(self.dbFile, "w") as f:
                f.write(json.dumps(self.db, indent=2, sort_keys=False))

    def load(self):
        with open(self.dbFile, "r") as f:
            self.db = json.load(f)

    def save(self):
        with open(self.dbFile, "w") as f:
            f.write(json.dumps(dict(self.db), indent=2, sort_keys=False))


class Logger:
    def __init__(self, name, path):
        if not os.path.isdir(f"{path}"):
            os.mkdir(f"{path}")
        LOGGER_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters':
            {
                'default':
                {
                    'format': "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                    'datefmt': "%H:%M:%S",
                },
            },
            'handlers':
            {
                'file':
                {
                    'level': 'DEBUG',
                    'formatter': 'default',
                    'class': 'logging.FileHandler',
                    'filename': f'{path}{name}.log',
                    'mode': 'w',
                },
                'screen':
                {
                    'level': 'INFO',
                    'formatter': 'default',
                    'class': 'logging.StreamHandler',
                },
            },
            'loggers':
            {
                '':
                {
                    'handlers': ['file', 'screen'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
            }
        }
        logging.config.dictConfig(LOGGER_CONFIG)
        #sys.excepthook = self._exceptHook

    def _exceptHook(self, type_, error, traceback):
        tb = traceback
        logging.critical(f"{type_} {error}".rstrip())
        while "tb_next" in dir(tb):
            logging.critical(f"{tb.tb_frame}")
            tb = tb.tb_next
        sys.__excepthook__(type_, error, traceback)  # Call default hook

    def new(self, name):
        return logging.getLogger(name)


class QDBusObject(QtCore.QObject):
    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.__dbusAdaptor = QDBusServerAdapter(self, parent)
        self.start()

    def start(self):
        bus = QtDBus.QDBusConnection.sessionBus()
        bus.registerObject(f"/org/{name}/session", self)
        bus.registerService(f"org.{name}.session")
        return bus


class QDBusServerAdapter(QtDBus.QDBusAbstractAdaptor):
    QtCore.Q_CLASSINFO("D-Bus Interface", f"org.{name}.session")
    QtCore.Q_CLASSINFO("D-Bus Introspection",
    f'<interface name="org.{name}.session">\n'
    '  <method name="parse">\n'
    '    <arg direction="in" type="s" name="cmd"/>\n'
    '  </method>\n'
    '</interface>\n')

    def __init__(self, server, parent):
        super().__init__(server)
        self.parent = parent

    @QtCore.pyqtSlot(str)
    def parse(self, cmd):
        # Serialize the string of commands
        if cmd:
            commands = {}
            current = ""
            for arg in cmd.split("%"):
                if arg.startswith("-"):
                    current = arg.lstrip("-")
                elif current:
                    commands[current].append(arg)
                if current not in commands:
                    commands[current] = []
            self.parent.parseCommands(commands)
