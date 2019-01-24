# -*- coding: UTF-8 -*-

import os
import time
import functools
import tushare as ts
import pandas as pd
import warnings
from datetime import datetime
from collections import OrderedDict
from zb.tools import pdf
from zb.tools import sms

from tma import data_path

# A股交易日历
# --------------------------------------------------------------------

FILE_CALENDAR = os.path.join(data_path, 'calendar.csv')
if os.path.exists(FILE_CALENDAR) and \
        time.time() - os.path.getmtime(FILE_CALENDAR) < 3600 * 24:
    trade_calendar = pd.read_csv(FILE_CALENDAR, encoding='utf-8')
else:
    trade_calendar = ts.trade_cal()  # tushare提供的交易日历
    trade_calendar.to_csv(FILE_CALENDAR, index=False, encoding='utf-8')


def is_trade_day(date):
    """判断date日期是不是交易日

    :param date: str or datetime.date, 如 2018-03-15
    :return: Bool
    """
    trade_day = trade_calendar[trade_calendar["isOpen"] == 1]
    trade_day_list = list(trade_day['calendarDate'])
    if isinstance(date, datetime):
        date = str(date.date())
    if date in trade_day_list:
        return True
    else:
        return False


def in_trade_time():
    """判断当前是否是交易时间"""
    today = str(datetime.now().date())
    if not is_trade_day(today):  # 如果今天不是交易日，返回False
        return False
    t1 = today + " " + "09:30:00"
    t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
    t2 = today + " " + "11:30:00"
    t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
    t3 = today + " " + "13:00:00"
    t3 = datetime.strptime(t3, "%Y-%m-%d %H:%M:%S")
    t4 = today + " " + "15:00:00"
    t4 = datetime.strptime(t4, "%Y-%m-%d %H:%M:%S")
    if t1 <= datetime.now() <= t2 or t3 <= datetime.now() <= t4:
        return True
    else:
        return False


def recent_trade_days(date, n=10):
    """返回任一日期date前后的n个交易日日期

    :param n: int
        返回交易日的数量n。
        如果 n > 0，则返回date日期未来的n个交易日日期；
        如果 n < 0，则返回date日期过去的n个交易日日期。
    :param date: str  默认值 today
    :return: list
        n个交易日日期列表
    """
    cal_date = list(trade_calendar['calendarDate'])
    date_index = cal_date.index(date)
    if n >= 0:
        recent_days = cal_date[date_index:date_index + n + 20]
    else:
        recent_days = cal_date[date_index + n - 20:date_index + 1]
        recent_days = recent_days[::-1]

    res = []
    for d in recent_days:
        if is_trade_day(d):
            res.append(d)
        if len(res) == abs(n):
            break
    return res


def run_at_trade_time(func):
    """控制函数func仅在交易时间段运行"""

    @functools.wraps(func)
    def wrapper(*args, **kw):
        if in_trade_time():
            res = func(*args, **kw)
        else:
            msg = "%s 不是交易时间，函数 %s 仅在交易时间执行" % (
                datetime.now().__str__(), func.__name__
            )
            warnings.warn(msg)
            res = None
        return res

    return wrapper


# 提取pdf中的文本
# --------------------------------------------------------------------
pdf2text = pdf.pdf2text


class OrderedAttrDict(OrderedDict):
    """可以通过 . 访问的有序字典"""
    def __init__(self, *args, **kwargs):
        super(OrderedAttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def convert_bool(condition):
    """True = 1, False = 0"""
    if condition:
        return 1
    else:
        return 0


server_chan_push = sms.server_chan_push
bear_push = sms.bear_push
EmailSender = sms.EmailSender


def send_email(from_, pw, to, subject, content, files=None, service='163'):
    """邮件发送（支持附件），推荐使用163邮箱"""
    se = EmailSender(from_=from_, pw=pw, service=service)
    se.send_email(to=to, subject=subject, content=content, files=files)
    se.quit()


def push2wx(send_key, by="bear"):
    """装饰器：推送消息到微信

    :param send_key: str
        用于发送消息的key
    :param by: str 默认值 bear
        发送消息的方式，默认是bear，
        可选值 ['bear', 'server_chan']
    :return:
    """
    def _wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            title, content = func(*args, **kw)
            if by == "bear":
                bear_push(title, content, send_key=send_key)
            elif by == "server_chan":
                server_chan_push(title, content, key=send_key)
            else:
                raise ValueError("参数by的可选值为 ['bear', 'server_chan']")
            return title, content
        return wrapper
    return _wrapper

