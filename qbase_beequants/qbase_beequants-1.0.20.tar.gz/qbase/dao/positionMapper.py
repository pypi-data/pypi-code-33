#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/8/22 上午11:12
# @Author  : datachain
import pandas as pd
from qbase.common import mySql
from qbase.common import configer as cf

positionRow = "id , account , strategy , symbol ,open_contract as openContract , start_base_coin as startBaseCoin, base_coin as baseCoin, base_coin_frozen as baseCoinFrozen , trade_coin as tradeCoin, trade_coin_frozen as tradeCoinFrozen,trade_contract as tradeContract, null_coin as nullCoin, null_coin_frozen as nullCoinFrozen ,null_contract as nullContract "
conf = cf.configer()

def getPosition(accountNo , strategy , symbol):
    db = mySql.Mysql(conf.getValueByKey("db", "ip"), int(conf.getValueByKey("db", "port")),
                     conf.getValueByKey("db", "userName"), conf.getValueByKey("db", "passwd"),
                     conf.getValueByKey("db", "dnName"))
    position = pd.read_sql(
        "select " + positionRow + " from position where account='" + accountNo + "' and strategy='"+strategy+"' and symbol='"+symbol+"' and status = 1", db.getDb())
    db.closeDb()
    if len(position) == 0:
        return None
    else:
        return position.iloc[0]


def setPosition(position):
    sql = "update position set "
    sql += "base_coin = " + str(position.baseCoin)
    sql += " , trade_coin = " + str(position.tradeCoin)
    sql += " , trade_contract = '" + str(position.tradeContract)
    sql += "' , null_coin = " + str(position.nullCoin)
    sql += " , null_contract = '" + str(position.nullContract)
    sql += "' where id = "+ str(position.id)
    # 链接数据库
    db = mySql.Mysql(conf.getValueByKey("db", "ip"), int(conf.getValueByKey("db", "port")),
                     conf.getValueByKey("db", "userName"), conf.getValueByKey("db", "passwd"),
                     conf.getValueByKey("db", "dnName"))
    result = db.modifyDb(sql)
    db.closeDb()
    return result

def setPositionFroze(position):
    sql = "update position set "
    sql += "base_coin_frozen = " + str(position.baseCoinFrozen)
    sql += " , trade_coin_frozen = " + str(position.tradeCoinFrozen)
    sql += " , null_coin_frozen = " + str(position.nullCoinFrozen)
    sql += " where id = " + str(position.id)
    # 链接数据库
    db = mySql.Mysql(conf.getValueByKey("db", "ip"), int(conf.getValueByKey("db", "port")),
                     conf.getValueByKey("db", "userName"), conf.getValueByKey("db", "passwd"),
                     conf.getValueByKey("db", "dnName"))
    result = db.modifyDb(sql)
    db.closeDb()
    return result