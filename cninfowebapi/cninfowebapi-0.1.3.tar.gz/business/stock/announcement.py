# -*- coding:utf-8 -*-
"""
FileName: announcement.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-28
Description: 公告相关接口
History: /*
 create 2019-01-28
 */
"""
import time
from dataapi.datamart import datamart
from business.stock.tradedate import gettradedates


def getannouncement(seccode='*', startdate='19900101',enddate=time.strftime('%Y%m%d',time.localtime())):
    """获取交易日区间"""
    if seccode == '*':
        return datamart.getapidata('p_info3015', paramsdict={'sdate': startdate, 'edate': enddate})
    else:
        return datamart.getapidata('p_info3015', paramsdict={'scode': seccode, 'sdate': startdate, 'edate': enddate})


if __name__ == '__main__':
    #df = getannouncement(seccode='000001', startdate='20190101', enddate='20190201')
    #df = getannouncement(startdate='20190126', enddate='20190128')
    datamart.apihelp('p_info3015')
    dfdatelist = gettradedates(startdate='20190120', enddate='20190129')
    for index, row in dfdatelist.iterrows():
        tdate = row["F001D"]
        getannouncement(startdate=tdate, enddate=tdate)
    #df = getannouncement(seccode='600001')
