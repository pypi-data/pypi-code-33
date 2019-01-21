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

xw =SenseDataService()

# res = xw.get_stock_price_day('000001', '2019-1-18')
res = xw.get_stock_price_tick_obj('000002')

print(res)

# print(res.other_name)