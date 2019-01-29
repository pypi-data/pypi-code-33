#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-8-6 15:40:03
# @Author  : datachain

from enum import Enum, unique

@unique
class AccountType(Enum):
    Futures = 'futures'
    Spot = 'spot'

@unique
class Exchange(Enum):
    HuoBi = 'huobi'
    OKEx = 'okex'
    BitMex = 'bitmex'

@unique
class TransactionResult(Enum):
    OK = {"code":1000 , "msg":"交易成功","data":{}}

    Fail = {"code":2000 , "msg":"交易失败","data":{}} #继续发
    CoinNumFail = {"code": 2001, "msg": "交易币数量不足", "data": {}} #不继续发
    NoCanPositionFail = {"code": 2002, "msg": "没有可以交易的仓位", "data": {}} #不继续发
    ResultOrderIdFail = {"code": 2003, "msg": "交易没有返回订单Id", "data": {}} #继续发


