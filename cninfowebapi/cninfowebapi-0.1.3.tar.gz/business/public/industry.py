# -*- coding:utf-8 -*-
"""
FileName: industry.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-28
Description: 行业分类信息
History: /*
 create 2019-01-29
 */
"""
from dataapi.datamart import datamart


def getareas():
    """获取地区分类信息"""
    return datamart.getapidata('p_public0003')

def getindustry(indtype):
    """获取行业分类信息"""
    """	008001	证监会行业分类标准 
    008002	巨潮行业分类标准 
    008003	申银万国行业分类标准 
    008004	新财富行业分类标准 
    008005	国资委行业分类标准 
    008006	巨潮产业细分标准 
    008007	天相行业分类标准 
    008008	全球行业分类标准"""
    return datamart.getapidata('p_public0002', paramsdict={'indtype': indtype})


if __name__ == '__main__':
    #getindustry('008001')
    datamart.apihelp('p_public0002')
    getareas()
