# -*- coding:utf-8 -*-
"""
FileName: baseinfo.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-28
Description: 股票基本信息相关接口
History: /*
 create 2019-01-28
 */
"""

from dataapi.datamart import datamart


def getstockinfos():
    """获取所有A股基本信息"""
    return datamart.getapidata('p_stock2101')

def getstocklist():
    """获取所有A股基本信息"""
    return datamart.getapidata('p_stock2101')["SECCODE"]

def getcompanyinfos():
    """获取所有公司基本信息"""
    return datamart.getapidata('p_stock2100', paramsdict={'scode': '000001,600000'})


if __name__ == '__main__':
    datamart.apihelp('p_stock2100')
    getcompanyinfos()
