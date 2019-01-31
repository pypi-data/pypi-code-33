# -*- coding: utf-8 -*-
"""
Created on Thu May  3 18:19:00 2018

@author: yili.peng
"""
from glob import glob

def detect_last_date(path):
    all_date=[int(path.split('.csv')[0].split('_')[-1]) for path in glob(path+'\\*_*.csv')]
    return max(all_date)