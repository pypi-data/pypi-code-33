# -*- coding:utf-8 -*-
"""
FileName: apitest.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-30
Description: 接口调用测试
History: /*
 create 2019-01-30
 */
"""
from dataapi.conf.clientinfo import SaveType
from dataapi.datamart import datamart
from business.stock.report import getprofit

if __name__ == "__main__":
    # 设置保存文件的类型 SaveType.JSON SaveType.CSV SaveType.EXCEL 文件默认保存到cninfo-data-platform/data/目录
    datamart.setSaveType(SaveType.NONE)
    # API帮助：查看API详细元数据信息
    datamart.apihelp('p_stock2301')
    # API调用方式一
    dfprofit = getprofit(scode='000001', rdate='20180930')
    # API调用方式二
    # datamart.getapidata('p_stock2301', paramsdict={'scode': '600001', 'rdate': '20180630', 'type': '071001'})

    # 以下是按照股票代码循环获取全市场财务数据
    """from business.stock.baseinfo import getstockinfos
    import time
    from dataapi.conf.requestparam import API_REQ_PAUSE
    dfcodelist = getstockinfos()
    for index, row in dfcodelist.iterrows():
        scode = row["SECCODE"]
        datamart.getapidata('p_stock2302', paramsdict={'scode': scode, 'rdate': '20180630', 'type': '071001'})
        #getprofit(scode=scode, rdate='20180930')
        time.sleep(API_REQ_PAUSE)"""
