#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/8/23 下午6:33
# @Author  : datachain
import pandas as pd
from qbase.common import mySql
from qbase.common import configer as cf
import time

def getTimeStamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp


okexResultRow = "position_id as positionId , order_id as orderId , amount , contract_name as contractName , create_date as createDate ,deal_amount as dealAmount , fee , price , price_avg as priceAvg , status ,symbol ,type ,unit_amount as unitAmount , lever_rate as leverRate "
okexResultInsert = "create_time, position_id, order_id, amount, contract_name, create_date, deal_amount, fee, price, price_avg, symbol, type,status, unit_amount, lever_rate"
conf = cf.configer()

def insertOkexResult(positionId ,okexResultJson):
    sql = "insert into okex_result ("+okexResultInsert+") VALUES ('"+str(getTimeStamp())+"' , "+str(positionId)+", '"+str(okexResultJson[u'order_id'])+"', '"+str(okexResultJson[u'size'])+"', '"+str(okexResultJson[u'instrument_id'])+"', '"+str(okexResultJson[u'timestamp'])+"', '"+str(okexResultJson[u'filled_qty'])+"', '"+str(okexResultJson[u'fee'])+"', "+str(okexResultJson[u'price'])+", '"+str(okexResultJson[u'price_avg'])+"', '"+str(okexResultJson[u'instrument_id'])+"', '"+str(okexResultJson[u'type'])+"', '"+str(okexResultJson[u'status'])+"', '"+str(okexResultJson[u'contract_val'])+"', "+str(okexResultJson[u'leverage'])+")"
    # 链接数据库
    db = mySql.Mysql(conf.getValueByKey("db", "ip"), int(conf.getValueByKey("db", "port")),
                     conf.getValueByKey("db", "userName"), conf.getValueByKey("db", "passwd"),
                     conf.getValueByKey("db", "dnName"))
    #print(sql)
    result = db.modifyDb(sql)
    db.closeDb()
    return result
