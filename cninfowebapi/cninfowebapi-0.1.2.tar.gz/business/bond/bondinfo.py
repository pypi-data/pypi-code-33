# -*- coding:utf-8 -*-
"""
FileName: bondinfo.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 债券基本信息
History: /*
 create 2019-01-29
 */
"""

from dataapi.datamart import datamart


def getbondcodemap(scode, sectype):
    """债券代码对照表"""
    return datamart.getapidata('p_bond2800', paramsdict={'scode': scode, 'sectype': sectype})

def getbondbaseinfo(scode):
    """获取债券基本信息数据"""
    return datamart.getapidata('p_bond2801', paramsdict={'scode': scode})


if __name__ == '__main__':
    datamart.apihelp('p_bond2800')
    getbondcodemap('00005', '002001')
