# -*- coding:utf-8 -*-
"""
FileName: tradedate.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-28
Description: 证券市场交易日信息
History: /*
 create 2019-01-28
 */
"""
from dataapi.datamart import datamart


def gettradedates(startdate='19900101',enddate='20301212'):
    """获取交易日区间"""
    return datamart.getapidata('p_public0001', paramsdict={'sdate': startdate, 'edate': enddate})


if __name__ == '__main__':
    datamart.apihelp('p_public0001')
    df = gettradedates('20190101', '20190201')
