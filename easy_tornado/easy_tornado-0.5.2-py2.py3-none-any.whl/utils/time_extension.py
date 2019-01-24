# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:28
from __future__ import division

import time

from .logging import it_print


def current_timestamp():
    """
    获取当前时间戳
    :return: 时间戳
    """
    return time.time()


def current_datetime(timestamp=None):
    """
    获取当前日期
    :param timestamp: 时间戳
    :return: 日期时间格式字符串 形如 2018-11-19 10:20:35
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def current_datetime_str(timestamp=None):
    """
    获取当前时间戳对应的日期时间字符串
    :param timestamp: 时间戳
    :return: 日期时间字符串 形如 20181119102035
    """
    return time.strftime("%Y%m%d%H%M%S", time.localtime(timestamp))


def current_datetime_str_s(timestamp=None):
    """
    获取当前时间戳对应的以T作为分割的日期、时间字符串
    :param timestamp: 时间戳
    :return: 日期时间字符串 形如 20181119T102035
    """
    return time.strftime("%Y%m%dT%H%M%S", time.localtime(timestamp))


class Timer(object):
    """
    计时器类
    """

    # 无效时间戳标志
    _invalid_ts = -1

    def __init__(self, debug=False):
        self._debug = debug
        self._start_ts = self._invalid_ts
        self._finish_ts = self._invalid_ts
        self.reset()

    def reset(self):
        """
        重新计时
        """
        self._start_ts = time.time()
        self._finish_ts = self._invalid_ts
        if self._debug:
            self.display_start('start at: ')

    @property
    def start_ts(self):
        return self._start_ts

    @property
    def finish_ts(self):
        return self._finish_ts

    def start(self):
        self.reset()
        return self.start_ts

    def finish(self):
        self._finish_ts = time.time()
        return self.finish_ts

    def cost(self):
        self._set_finish()
        return self._finish_ts - self._start_ts

    def display_start(self, msg=None):
        Timer._display_datetime(self._start_ts, msg)

    def display_finish(self, msg=None):
        self._set_finish()
        Timer._display_datetime(self._finish_ts, msg)

    def display_cost(self, msg=None):
        cost = self.cost()
        prefix = ''
        if msg:
            prefix = 'job [{}]'.format(msg)
        it_print('{} cost {} seconds'.format(prefix, cost))

    def _set_finish(self):
        if self._finish_ts == self._invalid_ts:
            self.finish()

    @staticmethod
    def _display_datetime(ts, msg=None):
        _tmp_msg = current_datetime(ts)
        if msg is not None:
            if not msg.endswith(' '):
                msg += ' '
            _tmp_msg = msg + _tmp_msg
        it_print(_tmp_msg)
