#  -*- coding: utf-8 -*-

'''

@desc: 日期时间工具类
@author: tony
@Date: 2018/12/26 下午4:55

'''

import traceback
import time
import datetime

from qdutils.common.stringutils import stringutils


class dateutils(object):
    """
        格式化字符串常量
    """
    FORMAT_MONTH = '%Y-%m'
    FORMAT_DAY = '%Y-%m-%d'
    FORMAT_HOUR = '%Y-%m-%d %H'
    FORMAT_MINUTE = '%Y-%m-%d %H:%M'
    FORMAT_SECOND = '%Y-%m-%d %H:%M:%S'
    FORMAT_MILLISECOND = '%Y-%m-%d %H:%M:%S.%f'
    FORMAT_TIME = '%H:%M:%S'
    FORMAT_SINGLE_HOUR = '%H'
    FORMAT_SINGLE_MINUTE = '%M'
    FORMAT_SINGLE_SECOND = '%S'
    FORMAT_SINGLE_MILLISECOND = '%f'

    @staticmethod
    def get_timestamp(time_str=None, format_str=None):
        """
            获取时间戳，默认当前点时间戳
        :param time_str:    时间 
        :param format_str:  格式化字符串
        :return:    整型时间戳
        """

        millis = 0
        if time_str:
            sdf = dateutils.FORMAT_SECOND
            if format_str:
                sdf = format_str
            try:
                timeArray = time.strptime(time_str, sdf)
                millis = int(time.mktime(timeArray))
                # millis = int(time.mktime(time.strptime(time_str, sdf)))
            except Exception:
                traceback.print_exc()
        else:
            millis = int(round(time.time()))
        return millis

    @staticmethod
    def get_datetime():
        """
        获取当前时间
        :return: datetime
        """
        return datetime.datetime.now()

    @staticmethod
    def get_datetime_string(format_str=FORMAT_SECOND):
        """
        获取当前时间
        :param format_str: 格式化字符串
        :return: 字符串，如2018-12-12 00:00:00
        """
        return datetime.datetime.now().strftime(format_str)

    @staticmethod
    def format_datetime_string(time_str=None, format_str=FORMAT_SECOND, replace_format_str=None):
        """
        格式化时间字符串
        :param time_str:  原始时间字符串，如2018-12-12 00:00:00 
        :param format_str:  原始时间格式化字符串
        :param replace_format_str: 新生成时间格式化字符串
        :return:    string 
        """
        new_datetime = None
        try:
            if time_str is None:
                new_datetime = dateutils.get_datetime().strftime(format_str)
            else:
                if replace_format_str is None:
                    new_datetime = datetime.datetime.strptime(time_str, format_str).strftime(format_str)
                else:
                    new_datetime = datetime.datetime.strptime(time_str, format_str).strftime(replace_format_str)
        except Exception:
            traceback.print_exc()
        return new_datetime

    @staticmethod
    def format_string_datetime(time_str=None, format_str=FORMAT_SECOND, replace_format_str=None):
        """
        格式化时间字符串
        :param time_str:  原始时间字符串，如2018-12-12 00:00:00 
        :param format_str:  原始时间格式化字符串
        :param replace_format_str: 新生成时间格式化字符串
        :return:    datetime.datetime
        """
        new_datetime = None
        try:
            if time_str is None:
                new_datetime = dateutils.get_datetime()
            else:
                if replace_format_str is None:
                    new_datetime = datetime.datetime.strptime(time_str, format_str)
                else:
                    new_time_str = dateutils.format_datetime_string(time_str, format_str, replace_format_str)
                    new_datetime = datetime.datetime.strptime(new_time_str, replace_format_str)
        except Exception:
            traceback.print_exc()
        return new_datetime

    @staticmethod
    def month_diff(n, time_str=None, old_format_str=FORMAT_MONTH, new_format_str=FORMAT_MONTH):
        """
        日期月加减
        :param n: 加减整数
        :param time_str: 原始时间字符串，如2018-12-12 00:00:00  
        :param old_format_str: 原始时间格式化字符串
        :param new_format_str: 新生成时间格式化字符串
        :return: 
        """
        datetime1 = None
        if time_str:
            datetime1 = dateutils.format_string_datetime(time_str, old_format_str)
        else:
            datetime1 = datetime.datetime.now()
        hour = datetime1.hour
        minute = datetime1.minute
        second = datetime1.second
        one_day = datetime.timedelta(days=1)
        q, r = divmod(datetime1.month + n, 12)
        datetime2 = datetime.datetime(
            datetime1.year + q, r + 1, 1, hour, minute, second) - one_day
        if datetime1.month != (datetime1 + one_day).month:
            return datetime2
        if datetime1.day >= datetime2.day:
            return datetime2
        return datetime2.replace(day=datetime1.day).strftime(new_format_str)

    @staticmethod
    def day_diff(n, time_str=None, old_format_str=FORMAT_DAY, new_format_str=FORMAT_DAY):
        """
        日期天加减
        :param n: 加减整数
        :param time_str: 原始时间字符串，如2018-12-12 00:00:00  
        :param old_format_str: 原始时间格式化字符串
        :param new_format_str: 新生成时间格式化字符串
        :return: 
        """
        get_time = None
        if time_str:
            get_time = dateutils.format_string_datetime(time_str, old_format_str)
        else:
            get_time = datetime.datetime.now()
        delta = get_time + datetime.timedelta(days=n)
        return delta.strftime(new_format_str)

    @staticmethod
    def hour_diff(n, time_str=None, old_format_str=FORMAT_HOUR, new_format_str=FORMAT_HOUR):
        """
        日期小时加减
        :param n: 加减整数
        :param time_str: 原始时间字符串，如2018-12-12 00:00:00  
        :param old_format_str: 原始时间格式化字符串
        :param new_format_str: 新生成时间格式化字符串
        :return: 
        """
        get_time = None
        if time_str:
            get_time = dateutils.format_string_datetime(time_str, old_format_str)
        else:
            get_time = datetime.datetime.now()
        delta = get_time + datetime.timedelta(hours=n)
        return delta.strftime(new_format_str)

    @staticmethod
    def minute_diff(n, time_str=None, old_format_str=FORMAT_HOUR, new_format_str=FORMAT_HOUR):
        """
        日期分钟加减
        :param n: 加减整数
        :param time_str: 原始时间字符串，如2018-12-12 00:00:00  
        :param old_format_str: 原始时间格式化字符串
        :param new_format_str: 新生成时间格式化字符串
        :return: 
        """
        get_time = None
        if time_str:
            get_time = dateutils.format_string_datetime(time_str, old_format_str)
        else:
            get_time = datetime.datetime.now()
        delta = get_time + datetime.timedelta(minutes=n)
        return delta.strftime(new_format_str)

    @staticmethod
    def second_diff(n, time_str=None, old_format_str=FORMAT_HOUR, new_format_str=FORMAT_HOUR):
        """
        日期秒加减
        :param n: 加减整数
        :param time_str: 原始时间字符串，如2018-12-12 00:00:00  
        :param old_format_str: 原始时间格式化字符串
        :param new_format_str: 新生成时间格式化字符串
        :return: 
        """
        get_time = None
        if time_str:
            get_time = dateutils.format_string_datetime(time_str, old_format_str)
        else:
            get_time = datetime.datetime.now()
        delta = get_time + datetime.timedelta(seconds=n)
        return delta.strftime(new_format_str)

    @staticmethod
    def get_day_list(start_day, end_day):
        """
        获取天时间段列表
        :param start_hour: 开始小时，如2018-12-11
        :param end_hour: 截至小时，如2018-12-12
        :return: ['2018-12-11','2018-12-12'] 
        """
        date_list = []
        if stringutils.not_empty(start_day) and stringutils.not_empty(end_day):
            begin_date = datetime.datetime.strptime(start_day, dateutils.FORMAT_DAY)
        end_date = datetime.datetime.strptime(end_day, dateutils.FORMAT_DAY)
        while begin_date <= end_date:
            date_str = begin_date.strftime(dateutils.FORMAT_DAY)
            date_list.append(date_str)
            begin_date += datetime.timedelta(days=1)
        return date_list

    @staticmethod
    def get_hour_list(start_hour, end_hour):
        """
        获取小时时间段列表
        :param start_hour: 开始小时，如2018-12-12 06
        :param end_hour: 截至小时，如2018-12-12 10
        :return: ['2018-12-12 06','2018-12-12 07'] 
        """
        hour_list = []
        d1 = dateutils.format_string_datetime(start_hour, dateutils.FORMAT_HOUR)
        d2 = dateutils.format_string_datetime(end_hour, dateutils.FORMAT_HOUR)
        stamp1 = time.mktime(d1.timetuple())
        stamp2 = time.mktime(d2.timetuple())
        if stamp1 <= stamp2:
            hours = long((stamp2 - stamp1) / (60 * 60))
            for i in range(0, hours + 1):
                d3 = d1 + datetime.timedelta(hours=i)
                hour_str = d3.strftime(dateutils.FORMAT_HOUR)
                hour_list.append(hour_str)
        return hour_list

    @staticmethod
    def get_diff_seconds(start_time, end_time, start_format_string=FORMAT_SECOND, end_format_string=FORMAT_SECOND):
        """
        :param start_time: 开始时间，如：2018-12-12 00:00:00
        :param end_time: 结束时间，如：2018-12-13 00:00:00
        :param start_format_string: 开始时间格式化字符串
        :param end_format_string: 结束时间格式化字符串
        :return: int
        """
        t1 = dateutils.get_timestamp(start_time, start_format_string)
        t2 = dateutils.get_timestamp(end_time, end_format_string)
        interval_time = t1 - t2
        return interval_time
