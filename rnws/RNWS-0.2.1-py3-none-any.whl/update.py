# -*- coding: utf-8 -*-
"""
Created on Thu May  3 18:21:21 2018

@author: yili.peng
"""

from WindPy import w
import pandas as pd
from .read import reading_data
from .cprint import cprint

def update_trading_date(start=20100101,end=20201231):
    w.start()
    dt_range=(start,end)
    time=pd.Series([int(dt.strftime('%Y%m%d')) for dt in w.tdays(str(dt_range[0]), str(dt_range[1]), "").Times])
    time.to_csv(reading_data.trading_dt_path,index=False)
    reading_data.trading_dt=time
    w.close()
    cprint('trading dt from %d to %d , if not enough please update'%(min(reading_data.trading_dt),max(reading_data.trading_dt)))