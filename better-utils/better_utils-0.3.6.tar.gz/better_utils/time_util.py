# -*- coding: utf-8 -*-
import calendar
import datetime
import re
import time


class TimeUtil:
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400

    @staticmethod
    def str_to_unix(s):
        '''
        任意字符串转unix时间戳 精确到秒
        :param s:
        :return:
        '''
        s = re.sub(r'[\s\-\\:]+', '', s)
        f = {
            "8": lambda x: int(time.mktime(time.strptime(x, "%Y%m%d"))),
            "10": lambda x: int(time.mktime(time.strptime(x, "%Y%m%d%H"))),
            "12": lambda x: int(time.mktime(time.strptime(x, "%Y%m%d%H%M"))),
            "14": lambda x: int(time.mktime(time.strptime(x, "%Y%m%d%H%M%S")))
        }.get(str(len(s)))
        assert f is not None, "日期格式非法"
        return f(s)

    @staticmethod
    def unix_to_str(u, p='%Y-%m-%d %H:%M:%S'):
        return time.strftime(p, time.localtime(u))

    @staticmethod
    def str_to_str(s, p):
        '''
        日期字符串互转
        :param s:
        :param p:
        :return:
        '''
        return time.strftime(p, time.localtime(TimeUtil.str_to_unix(s)))

    @staticmethod
    def getMonthFirstAndLastDay(s):
        '''
        当前日期所在月的第一天和最后一天
        :return:
        '''
        year = int(TimeUtil.str_to_str(s, "%Y"))
        month = int(TimeUtil.str_to_str(s, "%m"))
        weekDay, monthCountDay = calendar.monthrange(year, month)
        firstDay = datetime.date(year, month, day=1)
        lastDay = datetime.date(year, month, day=monthCountDay)
        firstDay = TimeUtil.str_to_str(str(firstDay), "%Y%m%d")
        lastDay = TimeUtil.str_to_str(str(lastDay), "%Y%m%d")
        return firstDay, lastDay

    @staticmethod
    def getWeekFirstAndLastDay(s):
        '''
        当前日期所在周的第一天和最后一天
        :return:
        '''
        d = datetime.datetime.strptime(TimeUtil.str_to_str(s, "%Y%m%d"), "%Y%m%d")
        firstDay = str(d - datetime.timedelta(days=d.weekday()))
        lastDay = str(d + datetime.timedelta(days=6 - d.weekday()))
        firstDay = TimeUtil.str_to_str(firstDay, "%Y%m%d")
        lastDay = TimeUtil.str_to_str(lastDay, "%Y%m%d")
        return firstDay, lastDay

    @staticmethod
    def now(p="%Y-%m-%d %H:%M:%S"):
        return TimeUtil.unix_to_str(TimeUtil.now_unix(), p)

    @staticmethod
    def now_unix():
        return int(time.time())
