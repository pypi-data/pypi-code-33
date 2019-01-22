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

class StockPriceTickObj(object):
    def __init__(self,dct):
        self.stock_code = dct['stock_code']
        self.name = dct['name']
        self.open_today = dct['open_today']
        self.close_last = dct['close_last']
        self.price_current = dct['price_current']
        self.price_high = dct['price_high']
        self.price_low = dct['price_low']
        self.bid_buy = dct['bid_buy']
        self.bid_sell = dct['bid_sell']
        self.deal_amount = dct['deal_amount']
        self.turnover = dct['turnover']
        self.buy_amount_1 = dct['buy_amount_1']
        self.buy_price_1 = dct['buy_price_1']
        self.buy_amount_2 = dct['buy_amount_2']
        self.buy_price_2 = dct['buy_price_2']
        self.buy_amount_3 = dct['buy_amount_3']
        self.buy_price_3 = dct['buy_price_3']
        self.buy_amount_4 = dct['buy_amount_4']
        self.buy_price_4 = dct['buy_price_4']
        self.buy_amount_5 = dct['buy_amount_5']
        self.buy_price_5 = dct['buy_price_5']
        self.sell_amount_1 = dct['sell_amount_1']
        self.sell_price_1 = dct['sell_price_1']
        self.sell_amount_2 = dct['sell_amount_2']
        self.sell_price_2 = dct['sell_price_2']
        self.sell_amount_3 = dct['sell_amount_3']
        self.sell_price_3 = dct['sell_price_3']
        self.sell_amount_4 = dct['sell_amount_4']
        self.sell_price_4 = dct['sell_price_4']
        self.sell_amount_5 = dct['sell_amount_5']
        self.sell_price_5 = dct['sell_price_5']
        self.trade_date = dct['trade_date']
        self.trade_time = dct['trade_time']

class CompanyInfoObj(object):
    def __init__(self,dct):
        self.stock_code = dct['stock_code']
        self.list_date = dct['list_date']
        self.market_status = dct['market_status']
        self.company_code = dct['company_code']
        self.company_name_full = dct['company_name_full']
        self.company_name = dct['company_name']
        self.region = dct['region']
        self.city = dct['city']
        self.register_address = dct['register_address']
        self.web = dct['web']
        self.profile = dct['profile']
        self.main_products = dct['main_products']
        self.business_scope = dct['business_scope']
        self.legal_represent = dct['legal_represent']
        self.chairman = dct['chairman']
        self.manager = dct['manager']

class StockPriceDayObj(object):
    def __init__(self,dct):
        self.stock_code = dct['stock_code']
        self.company_name = dct['company_name']
        self.time = dct['time']
        self.last_close = dct['last_close']
        self.open = dct['open']
        self.high = dct['high']
        self.low = dct['low']
        self.close = dct['close']
        self.before_open = dct['before_open']
        self.before_high = dct['before_high']
        self.before_low = dct['before_low']
        self.before_close = dct['before_close']
        self.after_open = dct['after_open']
        self.after_high = dct['after_high']
        self.after_low = dct['after_low']
        self.after_close = dct['after_close']
        self.volume = dct['volume']
        self.turnover = dct['turnover']
        self.change = dct['change']
        self.turn_rate = dct['turn_rate']

class CompanyAliasObj(object):
    def __init__(self,dct):
        # self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.company_name = dct['company_name']
        self.other_name = dct['other_name']

class SubcompanyInfoObj(object):
    def __init__(self, dct):
        self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.company_name = dct['company_name']
        self.sub_company_code = dct['sub_company_code']
        self.sub_company_name = dct['sub_company_name']
        self.industry_type = dct['industry_type']
