# -*- coding:utf-8 -*-
"""
FileName: neeqinfo.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 行情数据
History: /*
 create 2019-01-29
 */
"""

from dataapi.datamart import datamart


def getcompanyinfo(scode):
    """获取****数据"""
    return datamart.getapidata('p_neeq6002', paramsdict={'scode': scode})


if __name__ == '__main__':
    datamart.apihelp('p_neeq6002')
    getcompanyinfo(scode='430005')
