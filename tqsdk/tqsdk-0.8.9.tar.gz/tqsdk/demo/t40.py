#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'chengzhi'

from tqsdk import TqApi, TqSim

api = TqApi(TqSim())
# 获得 m1901 的持仓引用，当持仓有变化时 position 中的字段会对应更新
position = api.get_position("DCE.m1901")
# 获得资金账户引用，当账户有变化时 account 中的字段会对应更新
account = api.get_account()
# 下单并返回委托单的引用，当该委托单有变化时 order 中的字段会对应更新
order = api.insert_order(symbol="DCE.m1901", direction="BUY", offset="OPEN", volume=5)

while True:
    api.wait_update()
    if api.is_changing(order, ["status", "volume_orign", "volume_left"]):
        print("单状态: %s, 已成交: %d 手" % (order["status"], order["volume_orign"] - order["volume_left"]))
    if api.is_changing(position, "volume_long_today"):
        print("今多头: %d 手" % (position["volume_long_today"]))
    if api.is_changing(account, "available"):
        print("可用资金: %.2f" % (account["available"]))
