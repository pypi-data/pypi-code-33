
# encoding: utf-8

# =========================================
#       IMPORTS
# --------------------------------------

import rootpath

rootpath.append()

import re
import json
import logging
import coloredlogs
import mybad

from os import environ as env


# =========================================
#       CONSTANTS
# --------------------------------------

DISABLED_LOGLEVEL = 1000

DEFAULT_BASE_LOGGER = True
DEFAULT_BASE_LOGGER_FORMAT = '[%(name)s]: %(message)s'
DEFAULT_BASE_LOGGER_COLORS = True


# =========================================
#       ERRORS
# --------------------------------------

class MyBaseError(mybad.Error):
    pass


# =========================================
#       CLASSES
# --------------------------------------

class MyBase(object):

    def __init__(self,
        logger = None
    ):
        logger = self._get_logger(logger)

        self._logger = logger

    @property
    def logger(self):
        return self._logger

    def __repr__(self):
        pass # TODO

    def __str__(self):
        pass # TODO

    def __bool__(self):
        return True

    def __nonzero__(self):
        return self.__bool__()

    def __repr__(self):
        return '<{classname} logger={logger}>'.format(
            classname = self.__class__.__name__,
            logger = bool(self.logger),
        )

    def __str__(self):
        return '<{classname} logger={logger}>'.format(
            classname = self.__class__.__name__,
            logger = bool(self.logger),
        )

    # private

    def _get_logger(self, logger = None):
        prefix = '{name}'.format(
            name = self.__class__.__name__,
        )

        if logger is None:
            logger = logger or DEFAULT_BASE_LOGGER

        logging.basicConfig(
            format = DEFAULT_BASE_LOGGER_FORMAT,
        )

        if logger == False:
            logger = logging.getLogger(prefix)
            logger.setLevel(DISABLED_LOGLEVEL)

        else:
            if logger == True:
                logger = logging.getLogger(prefix)
            else:
                logger = logger

        colors = env.get('LOGGER_COLORS', None)
        colors = colors or env.get('COLORS', None)

        if colors is None:
            colors = DEFAULT_BASE_LOGGER_COLORS

        colors = re.search(r'^true|1$', str(colors), flags = re.IGNORECASE)

        if colors is None:
            colors = DEFAULT_BASE_LOGGER_COLORS

        if colors:
            coloredlogs.install(
                fmt = DEFAULT_BASE_LOGGER_FORMAT,
                logger = logger,
            )

        return logger


# =========================================
#       EXPORTS
# --------------------------------------

Base = MyBase
BaseError = MyBaseError
