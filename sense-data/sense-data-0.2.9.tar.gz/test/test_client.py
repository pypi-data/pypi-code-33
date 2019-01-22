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
from sense_data import *
import sense_core as sd
sd.log_init_config('settings', sd.config('log_path'))


def test_get_stock_price_tick():
    _xw = SenseDataService()
    _stock_code = '000005'
    res = _xw.get_stock_price_tick(_stock_code)
    print(res)
    print(res.trade_date)
    print(res.trade_time)

def test_get_stock_price_day():
    _xw = SenseDataService()
    _stock_code = '000002'
    res = _xw.get_stock_price_day(_stock_code, '2019-1-21')
    print(res)
    print(res.company_name)

def test_get_subcompany():
    _xw = SenseDataService()
    _stock_code = '000002'
    res = _xw.get_subcompany(_stock_code)
    print(res)
    print(res.company_name)

def test_get_company_info():
    _xw = SenseDataService()
    _stock_code = '000045'
    res = _xw.get_company_info(_stock_code)
    print(res)
    print(res.company_name)

def test_get_company_alias():
    _xw = SenseDataService()
    _stock_code = []
    res = _xw.get_company_alias(_stock_code)
    print(res)
    print(res[0].other_name)

