# -*- coding:utf-8 -*-
"""
FileName: nationaleconomy.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 国民经济与政府财政.
History: /*
 create 2019-01-29
 */
"""
from dataapi.datamart import datamart


def getgdp(year=None):
    """获取生产法国民生产总值"""
    if year is None:
        return datamart.getapidata('p_macro9056', paramsdict={})
    else:
        return datamart.getapidata('p_macro9056', paramsdict={'year': year})


if __name__ == '__main__':
    datamart.apihelp('p_macro9056')
    getgdp()
