#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that provides the API entrypoint for the py2log python package.
"""

import logging.config
import sys

try:
    import colorlog
except ImportError:
    colorlog = False

TRACE = 5


def configure(level=None, config=None, name=None, force=True):
    """
    Function that configures the python standard library logging package.

    Args:
        level (int, NoneType, optional):
        config (dict, NoneType, optional):
        name (str, NoneType, optional):
        force (bool, optional):
    """

    level = level or TRACE
    sys.excepthook = log_excepthook
    if force or not logging.root.handlers:
        configure_trace()

        logging_config = (
            config
            if config
            else {
                "disable_existing_loggers": False,
                "formatters": {
                    "console": {
                        "()": "colorlog.ColoredFormatter",
                        "datefmt": "%Y-%m-%d %H:%M:%S",
                        "format": "%(log_color)s%(lineno)-4d %(filename)-11s %(name)-17s %(funcName)-27s %(message)s",
                        "log_colors": {
                            "CRITICAL": "white,bold,bg_red",
                            "DEBUG": "cyan",
                            "ERROR": "red",
                            "INFO": "white",
                            "WARNING": "yellow",
                            "TRACE": "black,bold,bg_cyan",
                        },
                    },
                    "file": {
                        "datefmt": "%Y-%m-%d %H:%M:%S",
                        "format": "%(levelname)-8s %(lineno)-4d %(filename)-11s %(name)-17s %(funcName)-27s %(message)s",
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "console",
                        "level": 10,
                    },
                    "file": {
                        "class": "logging.FileHandler",
                        "filename": "pysdm.log",
                        "formatter": "file",
                        "level": 10,
                        "mode": "w",
                    },
                },
                "root": {"handlers": ["console", "file"], "level": 10},
                "version": 1,
            }
        )
        if not colorlog:
            logging_config["formatters"].pop("console", None)
            logging_config["handlers"]["console"]["formatter"] = "file"

        logging_config["handlers"]["console"]["level"] = level
        logging_config["handlers"]["file"]["level"] = level
        logging_config["root"]["level"] = level

        logging.config.dictConfig(logging_config)

    logger = logging.getLogger(name)
    logger.info("Successfully configured logging!")
    return logger


def configure_trace():
    """
    Function that configures a new TRACE log level.
    """

    logging.addLevelName(TRACE, "TRACE")
    logging.TRACE = TRACE
    logging.getLoggerClass().trace = log_trace_to_class
    logging.trace = log_trace_to_root


def log_excepthook(exc_type, exc_value, exc_traceback):
    """
    Function that automatically logs raised exceptions.

    Args:
        exc_type (type):
        exc_value (BaseException):
        exc_traceback (traceback):
    """

    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )


def log_trace_to_class(logger, message, *args, **kwargs):
    """
    Function that provides trace logging to a Logger class.

    Args:
        logger (logging.Logger):
        message (str): Log message.
        *args (list, optional): Variable length argument list.
        **kwargs (dict, optional): Arbitrary keyword arguments.
    """

    if logger.isEnabledFor(TRACE):

        # pylint: disable=protected-access
        logger._log(TRACE, message, args, **kwargs)


def log_trace_to_root(message, *args, **kwargs):
    """
    Function that provides trace logging to the root logger.

    Args:
        message (str): Log message.
        *args (list, optional): Variable length argument list.
        **kwargs (dict, optional): Arbitrary keyword arguments.
    """

    logging.log(TRACE, message, *args, **kwargs)
