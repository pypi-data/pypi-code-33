#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import traceback
import logging
import logging.handlers

from tomato.util import loadconf
from tomato.util.singleton import singleton


@singleton
class ColoredFormatter(logging.Formatter):
    '''A colorful formatter.'''
 
    def __init__(self, fmt = None, datefmt = None):
        logging.Formatter.__init__(self, fmt, datefmt)
 
    def format(self, record):
        # Color escape string
        COLOR_RED='\033[1;31m'
        COLOR_GREEN='\033[1;32m'
        COLOR_YELLOW='\033[1;33m'
        COLOR_BLUE='\033[1;34m'
        COLOR_PURPLE='\033[1;35m'
        COLOR_CYAN='\033[1;36m'
        COLOR_GRAY='\033[1;37m'
        COLOR_WHITE='\033[1;38m'
        COLOR_RESET='\033[1;0m'
        # Define log color
        LOG_COLORS = {
            'DEBUG': '%s',
            'INFO': COLOR_GREEN + '%s' + COLOR_RESET,
            'WARNING': COLOR_YELLOW + '%s' + COLOR_RESET,
            'ERROR': COLOR_RED + '%s' + COLOR_RESET,
            'CRITICAL': COLOR_RED + '%s' + COLOR_RESET,
            'EXCEPTION': COLOR_RED + '%s' + COLOR_RESET,
        }
        level_name = record.levelname
        msg = logging.Formatter.format(self, record)
        return LOG_COLORS.get(level_name, '%s') % msg

@singleton
class Log(object):

    def __init__(self, conf_file=None,
             filename=None,
             mode='a',
             cmdlevel='INFO',
             filelevel='INFO',
             cmdfmt = '[%(asctime)s] %(levelname)s %(process)d %(filename)s:%(lineno)d %(message)s',
             filefmt = '[%(asctime)s] %(levelname)s %(process)d %(filename)s:%(lineno)d %(message)s',
             cmddatefmt = '%Y-%m-%d %H:%M:%S',
             filedatefmt = '%Y-%m-%d %H:%M:%S',
             backup_count = 0, limit = 20480, when = None, colorful = False):

        logging.getLogger().level = logging.NOTSET
        # logging.debug('logger init...')

        self.filename = filename
        if conf_file != None:
            conf = loadconf(conf_file, raw=True)
            conf_items = dict(conf.items('settings'))
            if 'filename' in conf_items:
                self.filename = conf_items['filename']

        if self.filename is None:
            self.filename = getattr(sys.modules['__main__'], '__file__', 'log.py')
            self.filename = os.path.basename(self.filename.replace('.py', '.log'))

        if not os.path.exists(os.path.abspath(os.path.dirname(self.filename))):
            os.makedirs(os.path.abspath(os.path.dirname(self.filename)))
        self.mode = mode
        self.cmdlevel = cmdlevel
        self.filelevel = filelevel
        if isinstance(self.cmdlevel, str):
            self.cmdlevel = getattr(logging, self.cmdlevel.upper(), logging.DEBUG)
        if isinstance(self.filelevel, str):
            self.filelevel = getattr(logging, self.filelevel.upper(), logging.DEBUG)
        self.filefmt = filefmt
        self.cmdfmt = cmdfmt
        self.filedatefmt = filedatefmt
        self.cmddatefmt = cmddatefmt
        self.backup_count = backup_count
        self.limit = limit
        self.when = when
        self.colorful = colorful
        self.logger = None
        self.streamhandler = None
        self.filehandler = None
        self.set_logger(cmdlevel=self.cmdlevel)

        if conf_file != None:
            self.set_logger(mode=conf_items['mode'],
                            cmdlevel=conf_items['cmdlevel'],
                            filelevel=conf_items['filelevel'],
                            cmdfmt=conf_items['cmdfmt'],
                            filefmt=conf_items['filefmt'],
                            cmddatefmt=conf_items['cmddatefmt'],
                            filedatefmt=conf_items['filedatefmt'],
                            backup_count=int(conf_items['backup_count']),
                            when=conf_items['when'],
                            colorful=True)
        self.debug('logger initialization completed')

    def init_logger(self):
        '''Reload the logger.'''
        if self.logger is None:
            self.logger = logging.getLogger()
        else:
            logging.shutdown()

        self.logger.handlers = []
        self.streamhandler = None
        self.filehandler = None
        self.logger.setLevel(logging.DEBUG)
 
    def add_streamhandler(self):
        '''Add a stream handler to the logger.'''
        self.streamhandler = logging.StreamHandler()
        self.streamhandler.setLevel(self.cmdlevel)
        if self.colorful:
            formatter = ColoredFormatter(self.cmdfmt, self.cmddatefmt)
        else:
            formatter = logging.Formatter(self.cmdfmt, self.cmddatefmt,)
        self.streamhandler.setFormatter(formatter)
        self.logger.addHandler(self.streamhandler)

    def add_filehandler(self):
        '''Add a file handler to the logger.'''
        # Choose the filehandler based on the passed arguments
        if self.backup_count == 0: # Use FileHandler
            self.filehandler = logging.FileHandler(self.filename, self.mode)
        elif self.when is None:  # Use RotatingFileHandler
            self.filehandler = logging.handlers.RotatingFileHandler(self.filename,
                    self.mode, self.limit, self.backup_count)
        else: # Use TimedRotatingFileHandler
            self.filehandler = logging.handlers.TimedRotatingFileHandler(self.filename,
                    self.when, 1, self.backup_count)
        self.filehandler.setLevel(self.filelevel)
        formatter = logging.Formatter(self.filefmt, self.filedatefmt)
        self.filehandler.setFormatter(formatter)
        self.logger.addHandler(self.filehandler)
 
    def set_logger(self, **kwargs):
        '''Configure the logger.'''
        keys = ['mode','cmdlevel','filelevel','filefmt','cmdfmt',\
                'filedatefmt','cmddatefmt','backup_count','limit',\
                'when','colorful']
        for (key, value) in kwargs.items():
            if not (key in keys):
                return False
            setattr(self, key, value)
        if isinstance(self.cmdlevel, str):
            self.cmdlevel = getattr(logging, self.cmdlevel.upper(), logging.DEBUG)
        if isinstance(self.filelevel, str):
            self.filelevel = getattr(logging, self.filelevel.upper(), logging.DEBUG)
        if not "cmdfmt" in kwargs:
            self.filefmt='[%(asctime)s] %(filename)s line:%(lineno)d %(levelname)-8s%(message)s'
            self.filedatefmt = '%Y-%m-%d %H:%M:%S'
            self.cmdfmt='[%(asctime)s] %(filename)s line:%(lineno)d %(levelname)-8s%(message)s'
            self.cmddatefmt = '%Y-%m-%d %H:%M:%S'

        self.init_logger()
        self.add_streamhandler()
        self.add_filehandler()
        # Import the common log functions for convenient
        self.import_log_funcs()
        return True

    def import_log_funcs(self):
        '''Import the common log functions from the logger to the class'''
        log_funcs = ['debug', 'info', 'warning', 'error', 'critical',
                     'exception']
        for func_name in log_funcs:
            func = getattr(self.logger, func_name)
            setattr(self, func_name, func)

    def trace(self):
        info = sys.exc_info()
        for file, lineno, function, text in traceback.extract_tb(info[2]):
            self.error('%s line:%s in %s:%s' % (file, lineno, function, text))
        self.error('%s: %s' % info[:2])
