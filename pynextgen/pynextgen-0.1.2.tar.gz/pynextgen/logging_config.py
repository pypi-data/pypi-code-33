#! /usr/bin/env python

import logging
import logging.handlers
import os

from colorlog import ColoredFormatter

# TO avoid to have to import the logging library in the
# script/notebook calling get_logger

LOGGING_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def get_logger(f, n, log_level="debug", log_file="common.log", file_and_stream=True):
    """ Logging setup for all libraries
    """

    # In case logging is made from a jupyter notebook, f helps
    # pointing to the notebook importing the library (But don't
    # succeed now to get the name of the notebook in the logging
    # header)

    logger = logging.getLogger(os.path.basename(f) + " - " + n)
    logger.setLevel(LOGGING_LEVELS[log_level])

    handler = logging.FileHandler(os.path.expanduser(log_file))
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(funcName)s() - %(levelname)s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    if file_and_stream:
        handler_stream = logging.StreamHandler()
        handler_stream.setFormatter(formatter)
        logger.addHandler(handler_stream)

    return logger
