#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-8-6 15:40:03
# @Author  : datachain

from datetime import datetime, timedelta

"""
获取整点时间
num 整点参数
    num=1：获取一小整点
    mum=2：获取两小整点
    。。。
"""
def getWholeTime(curTime, num):
    #3600秒计算整点时间
    unit = 3600
    #截取计算得到整点时间
    wholeTime = curTime - (curTime % (unit * num))
    #取 3600*num 秒之后的整点时间
    nextWholeTime = wholeTime + unit * num
    return nextWholeTime

def parseUTC2TimestampInMinute(utc):
    """
    解析UTC时间
    :param utc: iso格式的时间字符串
            例如，2018-08-24T07:47:49.607Z
    :return: unix时间戳
    """
    utcTime = datetime.strptime(utc, "%Y-%m-%dT%H:%M:%S.%fZ")
    localtime = utcTime + timedelta(hours=8)
    format_str = "%Y-%m-%dT%H:%M:00"
    localtime = datetime.strptime(localtime.strftime(format_str), format_str)
    return int(localtime.timestamp())