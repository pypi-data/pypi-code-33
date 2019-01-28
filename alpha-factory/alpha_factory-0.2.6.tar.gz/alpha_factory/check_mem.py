# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 11:32:07 2018

@author: yili.peng
"""

import os
import psutil
import gc

def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss/1048576

def clean():
    gc.collect()

def get_memory_use_pct():
    return psutil.virtual_memory().percent

def get_memory_total():
    return psutil.virtual_memory().total/1048576