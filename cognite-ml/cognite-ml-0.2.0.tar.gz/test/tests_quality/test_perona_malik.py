#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt
import numpy as np
import os 
import pandas as pd
import sys


sys.path.append('../../')
from cognite.config import configure_session
from cognite.v05.timeseries import get_timeseries, get_datapoints_frame

from cognite_ml.filters import perona_malik



def regularity_metric(X):
    DX = X[1:]-X[:-1]
    N = len(DX)
    st = np.sum(1.0/N*np.abs(DX)**2)**0.5
    tv = 1.0/N*np.sum(np.abs(DX))

    return st, tv


def isGood(X, Y):
    Xst, Xtv = regularity_metric(X)
    Yst, Ytv = regularity_metric(Y)

    diff_st = Xst/Yst
    diff_tv = Xtv/Ytv
    
    if((np.abs(diff_st-1.0) <0.2) & (np.abs(diff_tv-1.0) >3.0)):
        res = True
    else:
        res = False

    return res
    
if __name__ == "__main__":    
    configure_session(os.environ.get('COGNITE_API_KEY'), 'akerbp')
    tag = 'VAL_10_PT_81608:VALUE'
    aggregates = ['totalvariation']
    start = datetime.datetime(2018, 6, 1)
    end   = datetime.datetime(2018, 7, 1)
    data = get_datapoints_frame([tag], start=start, end=end, granularity='1h', aggregates=aggregates)
    data = data.fillna(method='ffill')
    data = data.fillna(method='bfill')
    X = data[tag+'|totalvariation'].values
    is_of_quality = []
    for method in ['classic', 'exponential', 'tukey', 'guo','weikert']:
        Z = perona_malik(X, method=method, gradient_threshold=20, smoothing_factor=50)
        is_of_quality.append(isGood(X, Z))

    # Check the results 
    assert(is_of_quality == [False, True, True, False, False])