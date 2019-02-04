# -*- coding:utf-8 -*-
"""
FileName: fund.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 基金基本信息
History: /*
 create 2019-01-29
 */
"""

from dataapi.datamart import datamart


def getbaseinfo(scode=None, fundtype=None, investype=None, styleid=None, orgid=None):
    """获取基金基本数据"""
    if scode is not None:
        return datamart.getapidata('p_fund2600', paramsdict={'scode': scode})
    if fundtype is not None:
        return datamart.getapidata('p_fund2600', paramsdict={'fundtype': fundtype})
    if investype is not None:
        return datamart.getapidata('p_fund2600', paramsdict={'investype': investype})
    if styleid is not None:
        return datamart.getapidata('p_fund2600', paramsdict={'styleid': styleid})
    if orgid is not None:
        return datamart.getapidata('p_fund2600', paramsdict={'orgid': orgid})


if __name__ == '__main__':
    datamart.apihelp('p_fund2600')
    getbaseinfo(fundtype='003001')
