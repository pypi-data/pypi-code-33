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

class stock_price_tick(object):
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





