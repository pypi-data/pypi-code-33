# -*- coding:utf-8 -*-
"""
FileName: datehelper.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 日期处理辅助
History: /*
 create 2019-01-29
 */
"""
import time
from dateutil.parser import parse
from dataapi.conf.vars import DATETIME_FORMAT


def getlatesttimestr():
    return time.strftime(DATETIME_FORMAT)


def gettimedif(starttime, endtime):
    stime = parse(starttime)
    etime = parse(endtime)
    timedif = (etime-stime).total_seconds()
    return timedif


if __name__ == '__main__':
    timedif = gettimedif('2019-01-29 12:46:37', getlatesttimestr())
    print(timedif)


