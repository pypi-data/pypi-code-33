# -*- coding: UTF-8 -*-

"""
collector.cninfo - 采集巨潮咨询网的数据

官网：http://www.sse.com.cn/
====================================================================
"""

import requests
from datetime import datetime
from datetime import timedelta
import pandas as pd


def _parse_latest(url, params):
    announcements = []
    while True:
        params['pageNum'] += 1
        res = requests.post(url, data=params).json()
        for items in res['classifiedAnnouncements']:
            # print(item)
            for item in items:
                announcement = {
                    "url": "http://www.cninfo.com.cn/" + item['adjunctUrl'],
                    "title": item['announcementTitle'],
                    "date": datetime.fromtimestamp(
                        item['announcementTime'] / 1000).date().__str__(),
                    "code": item['secCode'],
                    "name": item['secName']
                }
                announcements.append(announcement)
        if not res['hasMore']:
            break
    return announcements


def get_sh_latest():
    """获取上交所的最新公告列表"""
    url = "http://www.cninfo.com.cn/cninfo-new/disclosure/sse_latest"
    params = {
        "column": "sse",
        "columnTitle": "沪市公告",
        "pageNum": 0,
        "pageSize": 30,
        "tabName": "latest"
    }
    announcements = _parse_latest(url, params)

    return pd.DataFrame(announcements)


def get_sz_latest():
    """获取深交所的最新公告列表"""
    url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/szse_latest'
    params = {
        "column": "szse",
        "columnTitle": "深市公告",
        "pageNum": 0,
        "pageSize": 30,
        "tabName": "latest"
    }
    announcements = _parse_latest(url, params)
    return pd.DataFrame(announcements)


def get_announcements(code, start=None, end=None):
    """获取指定股票一段时间内的所有公告

    :param code: str
        股票代码，如：600122
    :param start: str
        开始时间，如："20170810"，默认值为今日向前推 180天 的日期
    :param end: str
        结束时间，如："20180810"，默认值为今日日期
    :return: announcements
    """
    if not start:
        start_date = datetime.now().date() - timedelta(days=180)
    else:
        start_date = datetime.strptime(start, '%Y%m%d').date()

    if not end:
        end_date = datetime.now().date().__str__()
    else:
        end_date = datetime.strptime(end, '%Y%m%d').date()

    url = "http://www.cninfo.com.cn/cninfo-new/announcement/query"

    params = {
        "stock": code,
        "searchkey": None,
        "category": None,
        "pageNum": 0,
        "pageSize": 30,
        "column": "szse_gem",
        "tabName": "fulltext",
        "sortName": None,
        "sortType": None,
        "limit": None,
        "seDate": "%s ~ %s" % (str(start_date), str(end_date))
    }

    announcements = []

    while True:
        params['pageNum'] += 1
        res = requests.post(url, data=params).json()
        for item in res['announcements']:
            announcement = {
                "url": "http://www.cninfo.com.cn/" + item['adjunctUrl'],
                "title": item['announcementTitle'],
                "date": datetime.fromtimestamp(
                    item['announcementTime'] / 1000).date().__str__(),
                "code": item['secCode'],
                "name": item['secName']
            }
            announcements.append(announcement)
        if not res['hasMore']:
            break

    return pd.DataFrame(announcements)
