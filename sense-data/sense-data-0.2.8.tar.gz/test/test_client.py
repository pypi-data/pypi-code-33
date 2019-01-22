#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (C)2018 SenseDeal AI, Inc. All Rights Reserved
File: {name}.py
Author: xuwei
Email: weix@sensedeal.ai
Last modified: 2018.12.23
Description:
'''

import sense_core as sd
sd.log_init_config('settings', sd.config('log_path'))
from sense_data import *

def test_get_stock_price_tick():
    xw =SenseDataService()
    stock_code = '000005'
    res = xw.get_stock_price_tick(stock_code)
    print(res)
    print(res.trade_date)
    print(res.trade_time)

def test_get_stock_price_day():
    xw =SenseDataService()
    stock_code = '000002'
    res = xw.get_stock_price_day(stock_code, '2019-1-21')
    print(res)
    print(res.company_name)

def test_get_subcompany():
    xw =SenseDataService()
    stock_code = '000002'
    res = xw.get_subcompany(stock_code)
    print(res)
    print(res.company_name)