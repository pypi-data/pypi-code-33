# -*- coding:utf-8 -*-
"""
FileName: index.py
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


def getbaseinfo():
    """获取****数据"""
    return datamart.getapidata('p_stock2100', paramsdict={'scode': '000001,600000'})


if __name__ == '__main__':
    getbaseinfo()
