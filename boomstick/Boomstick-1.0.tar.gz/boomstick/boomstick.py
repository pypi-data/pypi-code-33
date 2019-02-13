"""
boomstick.py - Logging engine

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.MD
"""

import logging
import coloredlogs
from typing import Optional, Dict

# Log and Date Format
LOG_FORMAT = '<%(asctime)s %(name)s> [%(levelname)s] %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class Logger(logging.Logger):

    def __init__(self,
                 name,
                 logfile: Optional[str] = None,
                 level=logging.NOTSET,
                 log_format=LOG_FORMAT,
                 log_datefmt=DATE_FORMAT,
                 field_styles: Optional[Dict] = None,
                 level_styles: Optional[Dict] = None
                 ):
        super().__init__(name=name, level=level)

        # If a log file was specified, add a handler for it.
        if logfile:
            file_logger = logging.FileHandler(logfile, 'a', encoding="utf-8")
            file_logger_format = logging.Formatter(log_format)
            file_logger.setFormatter(file_logger_format)
            self.addHandler(file_logger)

        # set proper severity level
        self.setLevel(10)

        # add Console logging
        console = logging.StreamHandler()
        self.addHandler(console)

        # add console logging format
        console_format = logging.Formatter(log_format)

        # set console formatter to use our format.
        console.setFormatter(console_format)

        # coloredlogs hook
        if not level_styles:
            level_styles = {'critical': {'color': 'red', 'bold': True},
                            'error': {'color': 'red', 'bright': True},
                            'warning': {'color': 'yellow', 'bright': True},
                            'info': {'color': 'white', 'bright': True},
                            'debug': {'color': 'black', 'bright': True}}

        if not field_styles:
            field_styles = {'asctime': {'color': 'white', 'bright': True},
                            'levelname': {'color': 'white', 'bright': True},
                            'name': {'color': 'yellow', 'bright': True}}

        # coloredlogs hook
        coloredlogs.install(handler=name,
                            level=logging.DEBUG,
                            logger=self,
                            fmt=log_format,
                            level_styles=level_styles,
                            field_styles=field_styles,
                            datefmt=log_datefmt,
                            isatty=True,
                            )

        # disable propagation
        self.propagate = False

        self.info("Boomstick Loaded and ready for logging.")

    def demo(self):
        self.debug("Example Debug Statement")
        self.info("Example INFO Statement")
        self.warning("Example WARNING Statement")
        self.exception("Example EXCEPTION Statement")
        self.error("Example ERROR Statement")
