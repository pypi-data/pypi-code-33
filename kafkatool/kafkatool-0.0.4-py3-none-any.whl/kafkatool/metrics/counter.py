#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/24 7:00 PM 
# @Author : xbzheng

import json
from functools import partial
from collections import defaultdict
from structlog import get_logger
from threading import Timer, Thread
import datetime
import time
import atexit


class NothingCounter:
    __call__ = __getattr__ = lambda self, *_, **__: self


class LoopRunner(Thread):

    def __init__(self, func, interval=3):
        self._func = func
        self._interval = interval
        self._running = True
        super().__init__()

    def run(self):
        while self._running:
            time.sleep(self._interval)
            self._func()

    def exit(self, timeout=None):
        self._running = False
        self.join(timeout=timeout)


class Counter(defaultdict):
    """
    should call close() when not use
    """

    def __init__(self, verbose=True, report_interval=5):
        self.log = get_logger('Counter')
        super().__init__(int)
        if verbose and report_interval > 0:
            self._reporter = LoopRunner(self.report, report_interval)
            self._reporter.start()

    def incr(self, key, count: int = 1):
        """Increment a stat by `count`."""
        self[key] += count

    def decr(self, key, count: int = 1):
        """Decrement a stat by `count`."""
        self.incr(key, -count)

    def report(self):
        if len(self):
            self.log.info('metric report', ts=time.time(), **self)

    def reset(self):
        for k in self.keys():
            self[k] = 0

    def close(self):
        self._reporter.exit(timeout=5)
        self.report()
