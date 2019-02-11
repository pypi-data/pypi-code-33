# -*- coding:utf-8 -*-
"""
FileName: report.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-28
Description: 上市公司定期报告
History: /*
 create 2019-01-28
 */
"""
import time
from dataapi.datamart import datamart
from business.stock.baseinfo import getstockinfos
from dataapi.conf.requestparam import API_REQ_PAUSE
from dataapi.conf.clientinfo import SaveType

"""
071001:合并本期
071002:合并上期
071003:母公司本期
071004:母公司上期
"""
def getbalancesheet(scode, rdate='20180630',rtype='071001'):
    """上市公司资产负债表"""
    return datamart.getapidata('p_stock2300', paramsdict={'scode': scode, 'rdate': rdate, 'type': rtype})

def getcashflow(scode, rdate='20180630',rtype='071001'):
    """上市公司现金流表"""
    return datamart.getapidata('p_stock2302', paramsdict={'scode': scode, 'rdate': rdate, 'type': rtype})

def getprofit(scode, rdate='20180630',rtype='071001'):
    """上市公司利润表"""
    return datamart.getapidata('p_stock2301', paramsdict={'scode': scode, 'rdate': rdate, 'type': rtype})

def getindicators(scode, rdate='20180630',rtype='071001'):
    """上市公司利润表"""
    return datamart.getapidata('p_stock2303', paramsdict={'scode': scode, 'rdate': rdate, 'type': rtype})


if __name__ == '__main__':
    #df = getbalancesheet(scode='600000', rdate='20180630')
    #df = getcashflow(scode='600000', rdate='20180630')
    #df = getprofit(scode='600000', rdate='20180630')
    datamart.apihelp('p_stock2301')
    datamart.setSaveType(SaveType.CSV)
    getprofit(scode='000001', rdate='20180930')
    """dfcodelist = getstockinfos()
    for index, row in dfcodelist.iterrows():
        scode = row["SECCODE"]
        getprofit(scode=scode, rdate='20180930')
        time.sleep(API_REQ_PAUSE)"""
