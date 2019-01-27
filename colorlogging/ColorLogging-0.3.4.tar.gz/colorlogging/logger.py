#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  colorlogging/logger.py
#  v.0.3.4
#  Developed in 2019 by Travis Kessler <travis.j.kessler@gmail.com>
#
#  A simple Python logger with colored log levels
#

# Python stdlib imports
from inspect import currentframe, getframeinfo
import logging
import time
import copy
import os

# 3rd party imports
import colorama

# Log format (for stream output and file content)
LOG_FORMAT = '[%(asctime)s] [%(call_loc)s] [%(levelname)s] %(message)s'

# File format (timestamp.log)
FILE_FORMAT = '{}.log'.format(str(time.time()).split('.')[0])

# Colorama colors for log levels
COLORS = {
    logging.DEBUG: colorama.Fore.GREEN,
    logging.INFO: colorama.Fore.CYAN,
    logging.WARN: colorama.Fore.YELLOW,
    logging.ERROR: colorama.Fore.RED,
    logging.CRITICAL: colorama.Fore.LIGHTRED_EX
}


class ColorFormatter(logging.Formatter):
    '''Logging formatter for coloring log level in output stream'''

    def format(self, record, *args, **kwargs):

        if record.levelno not in COLORS.keys():
            raise ValueError(
                '{} not available for coloring'.format(record.levelname)
            )
        record_n = copy.copy(record)
        record_n.levelname = '{}{}{}'.format(
            COLORS[record_n.levelno],
            record_n.levelname,
            colorama.Style.RESET_ALL
        )
        return super(ColorFormatter, self).format(record_n, *args, **kwargs)


class ColorLogger:

    def __init__(self, stream_level='debug', file_level='disable',
                 log_dir='logs', use_color=True, name='color_logger'):
        '''Color logger: colors log levels in output stream

        Args:
            log_dir (str): path to directory where logs are saved
            stream_level (str): log level for stream output
            file_level (None or str): log level for file output; defaults to
                disabling file logging
            use_color (bool): whether or not to color stream logs
            name (str): name of the logger
        '''

        # Colorama has a bug on Windows
        if os.name == 'nt':
            use_color = False
        if use_color:
            colorama.init()

        self.__log_dir = log_dir

        # If a ColorLogger already exists, get it. Otherwise, create one.
        self.__stream_logger = logging.getLogger(name + '_stream')
        if file_level != 'disable':
            self.__file_logger = logging.getLogger(name + '_file')

        if len(self.__stream_logger.handlers) == 0:

            s_handler = logging.StreamHandler()
            if use_color:
                s_handler.setFormatter(ColorFormatter(LOG_FORMAT, '%H:%M:%S'))
            else:
                s_handler.setFormatter(
                    logging.Formatter(LOG_FORMAT, '%H:%M:%S')
                )

            self.__stream_logger = logging.Logger(name + '_stream')
            self.__stream_logger.addHandler(s_handler)

            self.__file_logger = logging.Logger(name + '_file')
            if file_level != 'disable':
                self.__add_file_handler()

        self.__levels = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARN,
            'warn': logging.WARN,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
            'crit': logging.CRITICAL,
            'disable': None
        }

        self.__stream_fns = {
            'debug': self.__stream_logger.debug,
            'info': self.__stream_logger.info,
            'warning': self.__stream_logger.warning,
            'warn': self.__stream_logger.warning,
            'error': self.__stream_logger.error,
            'critical': self.__stream_logger.critical,
            'crit': self.__stream_logger.critical
        }

        self.__file_fns = {
            'debug': self.__file_logger.debug,
            'info': self.__file_logger.info,
            'warning': self.__file_logger.warning,
            'warn': self.__file_logger.warning,
            'error': self.__file_logger.error,
            'critical': self.__file_logger.critical,
            'crit': self.__file_logger.critical
        }

        self.stream_level = stream_level
        self.file_level = file_level

    @property
    def stream_level(self):
        '''Returns current level of stream logger'''

        if self.__stream_logger.disabled:
            return 'disable'
        return logging.getLevelName(
            self.__stream_logger.getEffectiveLevel()
        ).lower()

    @stream_level.setter
    def stream_level(self, level):
        '''Args:
            level (str): desired log level
        '''

        if level not in self.__levels.keys():
            raise ValueError('{} is not a valid log level'.format(level))
        if level == 'disable':
            self.__stream_logger.disabled = True
        else:
            self.__stream_logger.disabled = False
            self.__stream_logger.setLevel(self.__levels[level])

    @property
    def file_level(self):
        '''Returns current level of file logger'''

        if self.__file_logger.disabled:
            return 'disable'
        return logging.getLevelName(
            self.__file_logger.getEffectiveLevel()
        ).lower()

    @file_level.setter
    def file_level(self, level):
        '''Args:
            level (str): desired log level
        '''

        if level not in self.__levels.keys():
            raise ValueError('{} is not a valid log level'.format(level))
        if level == 'disable':
            self.__file_logger.disabled = True
        else:
            if self.__file_logger.disabled:
                self.__add_file_handler()
            self.__file_logger.disabled = False
            self.__file_logger.setLevel(self.__levels[level])

    @property
    def log_dir(self):
        '''Returns str: path to file logging directory'''

        return self.__log_dir

    @log_dir.setter
    def log_dir(self, log_dir):
        '''Args:
            log_dir (str): path to desired file logging directory
        '''

        self.__log_dir = log_dir
        self.__add_file_handler()

    def log(self, level, message, call_loc=None):
        '''Log a message

        Args:
            level (str): level to log the message at
            message (str): message to log
            call_loc (str): location where the log occurred; if None, defaults
                to 'function:lineno'
        '''

        if level not in self.__stream_fns.keys():
            raise ValueError('{} not a valid logging level'.format(level))

        if call_loc is None:
            call_loc = {'call_loc': '{}:{}'.format(
                getframeinfo(currentframe().f_back).function,
                getframeinfo(currentframe().f_back).lineno
            )}
        else:
            call_loc = {'call_loc': call_loc}

        self.__stream_fns[level](message, extra=call_loc)
        if not self.__file_logger.disabled:
            self.__file_fns[level](message, extra=call_loc)

    def __add_file_handler(self):
        '''Private method: adds handler to ColorLogger for file logging, creates
        directory
        '''

        if not os.path.exists(self.__log_dir):
            os.mkdir(self.__log_dir)
        if len(self.__file_logger.handlers) != 0:
            self.__file_logger.handlers = []
        f_handler = logging.FileHandler(
            os.path.join(self.__log_dir, FILE_FORMAT)
        )
        f_handler.setFormatter(
            logging.Formatter(LOG_FORMAT, '%H:%M:%S')
        )
        self.__file_logger.addHandler(f_handler)


def log(level, message, name='color_logger', to_file=False, log_dir='logs',
        use_color=True, call_loc=None):
    '''Simple logging: logging without initializing a ColorLogger object

    Args:
        level (str): level to log the message at
        message (str): message to log
        name (str): name of the logger
        to_file (bool): if True, logs message to file
        log_dir (str): path to directory where logs are saved if file logging
        use_color (bool): whether or not to color stream logs
        call_loc (str): location where the log occurred; if None, defaults to
            'function:lineno'
    '''

    if call_loc is None:
        call_loc = '{}:{}'.format(
            getframeinfo(currentframe().f_back).function,
            getframeinfo(currentframe().f_back).lineno
        )
    file_level = 'disable'
    if to_file:
        file_level = 'debug'
    logger = ColorLogger(
        file_level=file_level,
        log_dir=log_dir,
        name=name,
        use_color=use_color
    )
    logger.log(level, message, call_loc=call_loc)
