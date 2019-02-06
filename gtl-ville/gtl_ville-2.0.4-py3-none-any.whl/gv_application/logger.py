#!/usr/bin/env python3


import logging as logging
from logging import handlers
import os


class GVLogger(logging.Logger):

    def __init__(self, name, logdir):
        super().__init__(name=name, level=logging.DEBUG)

        # create console handler and set level to info
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create file handler and set level to debug
        logfile = os.path.join(logdir, name + '.log')
        fh = handlers.TimedRotatingFileHandler(filename=logfile, when='D', interval=1, backupCount=6)
        fh.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch and fh
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # add ch and fh to logger
        self.addHandler(ch)
        self.addHandler(fh)
