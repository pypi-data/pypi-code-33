from typing import Dict

import sys

from logging import getLogger, StreamHandler, Formatter, getLevelName, Logger as _Logger
from os.path import abspath, dirname, isdir
from subprocess import Popen, PIPE
from collections import namedtuple
from os import makedirs

from bgez.system import python

from . import logging_server

import bgez

__all__ = [
    'get_logger',
    'get_loggers',
    'LoggerStream',
    'LogfileHandler',
    'BaseLogger',
    'Logger',
    'ChildLogger',
]

FORMAT = Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
LOGGERS: Dict[str, 'BaseLogger'] = {} # Dictionnary storing loggers by their name.

def get_logger(name: str) -> 'BaseLogger':
    '''
    Returns the logger corresponding to `name`. If no logger with `name` already exists, it's
    created. Like in the default logging module you can create child loggers ("A.B.C"), but it
    will automatically create its parent if it doesn't exist yet.

    Note: Child loggers mentionned above are custom loggers, see ChildLogger for more information.
    '''
    logger = LOGGERS.get(name, None)
    if logger is not None:
        return logger

    if "." in name:
        parent_name = name[:name.rfind(".")]
        parent = get_logger(parent_name)
        logger = ChildLogger(name, parent)
    else:
        logger = Logger(name)

    LOGGERS[name] = logger
    return logger

def get_loggers():
    return LOGGERS.items()


class LoggerStream:
    '''
    Python's logging's StreamHandler don't handle encoding so this wrapper encodes the payload before
    sending it. It only takes a stream as argument, the same you would give to a StreamHandler.
    '''

    def __init__(self, stream):
        self.__stream = stream
        self.name = str(stream.name)

    def write(self, message):
        '''Writes the given message once encoded.'''
        self.__stream.write(message.encode("utf-8"))

    def __getattr__(self, attr_name):
        return getattr(self.__stream, attr_name)

class LogfileHandler(StreamHandler):
    '''
    Handler that sends its logs to a subprocess which writes them in `logfile_path`. When started,
    it saves a backup of last logfile up to `backups` backups.
    Note: `logfile_path` must be a full path and the last element must be the logfile's name.
    '''

    def __init__(self, logfile_path, backups):
        logfile_path = abspath(logfile_path)
        self.__srv = self.__start_server(logfile_path, backups)
        super().__init__(LoggerStream(self.__srv.stdin))

    def __start_server(self, logs_path, backups):
        '''Starts the log server in a subprocess.'''
        logs_folder = dirname(logs_path)
        if not isdir(logs_folder):
            makedirs(logs_folder)

        return Popen(
            [python, abspath(logging_server.__file__), logs_path, str(backups)],
            cwd=bgez.project, stdin=PIPE, bufsize=0
        )

class BaseLogger:
    '''Base class for loggers. It only implements aliases for convenience.'''

    _logger: _Logger
    name: str

    def __init__(self):
        raise NotImplementedError()

    def isLevel(self, level):
        return self._logger.isEnabledFor(level)

    def getLevel(self):
        return self._logger.getEffectiveLevel()

    def getLevelName(self):
        return getLevelName(self.getLevel())

    def child(self, name: str):
        return get_logger(f'{self.name}.{name}')

    def info(self, *args, **kargs):
        return self._logger.info(*args, **kargs)

    def warning(self, *args, **kargs):
        return self._logger.warning(*args, **kargs)

    def debug(self, *args, **kargs):
        return self._logger.debug(*args, **kargs)

    def error(self, *args, **kargs):
        return self._logger.error(*args, **kargs)

    def critical(self, *args, **kargs):
        return self._logger.critical(*args, **kargs)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} [{self.getLevelName()}]>"

class Logger(BaseLogger):
    '''
    Wrapper around a regular logger instance. As is, it as offers nothing more than a regular
    logger, but it has built-in abilities to redirect its logs to any stream (file-like objects,
    stderr, stdout, etc) and/or to any logging server (see `add_stream` and `add_server`).

    Note: Built-in handlers' severity level is set to the one of their logger when created, but
    like any handler, you can set their own severity level by calling `setLevel` on them.

    Note 2: The severity level set on the logger filters what messages it'll give to its handlers.
    to set a severity level for a peculiar handler, call `setLevel` on the handler itself. This way,
    you can fully disable the logger by setting it a high severity level.
    '''

    __reg_items = namedtuple("RegistryItems", "logger handler")

    def __init__(self, name):
        self._logger = getLogger(name)

    def add_server(self, logfile_path, backups=5):
        '''
        Creates a handler that sends its logs to a logging in a subprocess. Logs are saved in the
        file at `logfile_path` and, at startup, a backup of the last logfile is created, up to
        `backups` backups.

        Returns a tuple containing a logger and the handler. If an existing handler is already
        writing logs at `logfile_path`, the logger returned in the tuple is the logger owning
        this handler.

        See LogfileHandler and logging_server.py for more information.
        '''
        return self._add_handler("logfiles", LogfileHandler, abspath(logfile_path), backups)

    def add_stream(self, stream=sys.stderr):
        '''
        Creates a handler that sends it logs to `stream` (file-like object, stderr, stdout, etc).

        Returns a tuple containing a logger and the handler. If an existing handler is already
        writing logs on `stream`, the logger returned in the tuple is the logger owning this
        handler.
        '''
        return self._add_handler("streams", StreamHandler, stream)

    def _add_handler(self, registry_name, handler_class, key, *args, **kargs):
        '''Creates and configure a handler of class `handler_class`.'''

        if hasattr(self.__class__, registry_name):
            registry = getattr(self.__class__, registry_name)
            logger_handler = registry.get(key, None)
            if logger_handler is not None: return logger_handler
        else:
            registry = {}
            setattr(self.__class__, registry_name, registry)

        handler = handler_class(key, *args, **kargs)
        handler.setFormatter(FORMAT)
        handler.setLevel(self.getLevel())
        self._logger.addHandler(handler)

        logger_handler = self.__reg_items(self, handler)
        registry[key] = logger_handler
        return logger_handler

    def __getattr__(self, attr_name):
        return getattr(self._logger, attr_name)

class ChildLogger(BaseLogger):
    '''
    Dumb logger which sends its log to its parent if its severity allows it. It means that
    a message logged via a child will truly be logged if and only if all parent loggers accept
    it, which is NOT the default behaviour of Python's logging module.
    '''

    def __init__(self, name, parent):
        self._logger = getLogger(name)
        self.__parent = parent

    def _log(self, *args, **kargs):
        self.__parent.log(*args, **kargs)

    def __getattr__(self, attr_name):
        return getattr(self._logger, attr_name)
