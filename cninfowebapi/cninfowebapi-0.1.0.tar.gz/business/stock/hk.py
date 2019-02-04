# -*- coding:utf-8 -*-
"""
FileName: hk.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 港股
History: /*
 create 2019-01-29
 */
"""

from dataapi.datamart import datamart


def getbaseinfo(scode):
    """获取港股公司概况数据"""
    return datamart.getapidata('p_hk4001', paramsdict={'scode': scode})


if __name__ == '__main__':
    datamart.apihelp('p_hk4001')
    getbaseinfo(scode='00001')
