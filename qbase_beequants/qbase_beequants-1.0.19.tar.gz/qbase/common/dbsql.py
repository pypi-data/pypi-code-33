#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019/1/2
# @Author  : beequants-nick


import pandas as pd
from qbase.common import mySql
from qbase.common import configer as cf
import logging

log = logging.getLogger()
conf = cf.configer()
klineRow = "created_date/1000 as created_date, open, high, low, close, volume, currency_volume, symbol"


def get_kline_list(start_time, end_time, symbol, period, num=None):
    db = mySql.Mysql(conf.getValueByKey("dbData", "ip"), int(conf.getValueByKey("dbData", "port")),
                     conf.getValueByKey("dbData", "userName"), conf.getValueByKey("dbData", "passwd"),
                     conf.getValueByKey("dbData", "dnName"))
    sql = "select " + klineRow + " from okex_futures_kline_%s where symbol = '" % period + symbol + "_usd' "
    if start_time is not None and end_time is not None:
        sql += " and created_date between unix_timestamp('%s')*1000 and unix_timestamp('%s')*1000 " % (start_time, end_time)
    sql += " order by created_date desc"
    if num is not None:
        sql += " limit %s" % num
    kline = pd.read_sql(sql, db.getDb())
    db.closeDb()
    return kline


def get_tick_kline_list(symbol, tick, period, expr=3, unit='day'):
    col_row = "t1.created_date/1000 tick_date,t1.close tick_close,t2.created_date/1000 created_date,t2.open,t2.high, t2.low, t2.close, t2.volume, t2.currency_volume, t2.symbol"
    sub_col_row = "*,CEILING(created_date/(60*60*4*1000)-2)*60*60*4*1000 tick_date"

    db = mySql.Mysql(conf.getValueByKey("dbData", "ip"), int(conf.getValueByKey("dbData", "port")),
                     conf.getValueByKey("dbData", "userName"), conf.getValueByKey("dbData", "passwd"),
                     conf.getValueByKey("dbData", "dnName"))
    
    sql = "select " + col_row + " from ( "
    sql += "SELECT "+sub_col_row+" from okex_futures_kline_%s " % tick
    sql += "where created_date > UNIX_TIMESTAMP( DATE_SUB(NOW(),INTERVAL %s %s))*1000 ) t1, " % (expr, unit)
    sql += "(SELECT * from okex_futures_kline_%s " % period
    sql += "where created_date > UNIX_TIMESTAMP( DATE_SUB(NOW(),INTERVAL %s %s))*1000 ) t2 " % (expr, unit)
    sql += "where t1.tick_date = t2.created_date "
    sql += "and t1.symbol = t2.symbol "
    sql += "and t1.symbol = '%s_usd' " % symbol
    sql += "ORDER BY tick_date asc "
    kline = pd.read_sql(sql, db.getDb())
    db.closeDb()
    return kline
