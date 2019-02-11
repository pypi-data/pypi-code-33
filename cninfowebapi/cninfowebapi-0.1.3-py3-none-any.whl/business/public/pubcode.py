# -*- coding:utf-8 -*-
"""
FileName: industry.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-29
Description: 公共编码
History: /*
 create 2019-01-29
 */
"""
from dataapi.datamart import datamart


def getpubcodes(subtype):
    """获取地区分类信息
    @:param subtype:string 总类编码,如001
    """
    return datamart.getapidata('p_public0006', paramsdict={'subtype': subtype})


if __name__ == '__main__':
    datamart.apihelp('p_public0006')
    getpubcodes(subtype='001')
