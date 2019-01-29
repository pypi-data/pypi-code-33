#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/8/22 上午11:11
# @Author  : datachain
import pandas as pd
from qbase.common import mySql
from qbase.common import configer as cf




accountRow = "id , exchange , access_key as accessKey , secret_key as secretKey , passphrase as passphrase, spot_account as spotAccount ,futures_account as futuresAccount , other_account as otherAccount , status "
conf = cf.configer()

def getAccountByExchange(exchange):
    db = mySql.Mysql(conf.getValueByKey("db", "ip"), int(conf.getValueByKey("db", "port")),
                     conf.getValueByKey("db", "userName"), conf.getValueByKey("db", "passwd"),
                     conf.getValueByKey("db", "dnName"))
    accountList = pd.read_sql("select "+ accountRow + " from account where exchange='"+exchange+"' and status = 1 ",db.getDb())
    db.closeDb()
    return accountList