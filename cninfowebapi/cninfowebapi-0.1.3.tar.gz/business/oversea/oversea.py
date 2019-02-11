# -*- coding:utf-8 -*-
"""
FileName: oversea.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 海外数据
History: /*
 create 2019-01-29
 */
"""

from dataapi.datamart import datamart


def getbaseinfo(scode='00001-HKG'):
    """获取基金基本数据"""
    if scode is not None:
        return datamart.getapidata('p_GSCI8203', paramsdict={'scode': scode})


if __name__ == '__main__':
    datamart.apihelp('p_GSCI8203')
    getbaseinfo(scode='00001-HKG')
