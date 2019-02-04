# -*- coding:utf-8 -*-
"""
FileName: english.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 英文接口数据
History: /*
 create 2019-01-29
 */
"""

from dataapi.datamart import datamart


def getcompanyinfo(scode):
    """Basic Information about Listed Companies"""
    return datamart.getapidata('p_en7001', paramsdict={'scode': scode})


if __name__ == '__main__':
    datamart.apihelp('p_en7001')
    getcompanyinfo('000001')
