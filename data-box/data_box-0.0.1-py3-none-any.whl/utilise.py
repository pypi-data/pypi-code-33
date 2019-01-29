# -*- coding: utf-8 -*-
"""
Created on Tue May  8 13:30:40 2018

@author: yili.peng
"""
import time
from functools import reduce
from copy import deepcopy
import numpy as np
from datetime import datetime
from functools import wraps
import warnings
def pre_sus(x):
    '''
    for new stocks detection and recording
    '''
    y=deepcopy(x)
    if x.isnull().any():
        i=np.where(x.isnull())[0][-1]  
        if i==0:
            y.iloc[i:(i+20)]=1
        y.fillna(1,inplace=True) 
    return y

def change_index(df,date_type='%Y%m%d'):
    df1=df.copy()
    try:        
        df1.index=[datetime.strptime(str(t),date_type) for t in df1.index]
    except:
        print('index is not valid for strptime')        
    return df1.rename_axis('dt').rename_axis('ticker',axis=1)

def monthmove(ym,delta=1):
    y=int(ym)//100
    m=int(ym)%100
    ny=y+(m-1+delta)//12
    nm=(m-1+delta)%12+1
    return str(int(ny*100+nm))

def check_time(dt1):
    dt=dt1
    while True:
        try:
            datetime.strptime(str(dt),'%Y%m%d')
            break
        except:
            dt=int(dt)-1
            if dt%100==0:
                raise Exception('Wrong dt at check_time')
    return datetime.strptime(str(dt),'%Y%m%d')


class ci_transformer:
    def __init__(self):
        self.columns=None
        self.index=None
    def fit_columns(self,*args):
        l=[]
        for a in args:
            if a is None:
                continue
            else:
                l.append(a.columns)
        a=list(reduce(lambda x,y: set(x)&set(y),l))
        a.sort()
        self.columns=a
    def fit_index(self,*args):
        l=[]
        for a in args:
            if a is None:
                continue
            else:
                l.append(a.index)
        a=list(reduce(lambda x,y: set(x)&set(y),l))
        a.sort()
        self.index=a
    def fit(self,*args):
        self.fit_columns(*args)
        self.fit_index(*args)
    def transform_columns(self,*args):
        l=[]
        for a in args:
            if a is None:
                l.append(a)
            else:
                l.append(a.reindex(columns=self.columns))
        return l
    def transform_index(self,*args):
        l=[]
        for a in args:
            if a is None:
                l.append(a)
            else:
                l.append(a.reindex(index=self.index))
        return l
    def transform(self,*args):
        l=[]
        for a in args:
            if a is None:
                l.append(a)
            else:
                l.append(a.reindex(index=self.index,columns=self.columns))
        return l

def easy_regression(factor,size):
    warnings.filterwarnings('ignore')
    x = np.asarray(size)
    y = np.asarray(factor)
    xmean = np.mean(x, None)
    ymean = np.mean(y, None)
    ssxm, ssxym, ssyxm, ssym = np.cov(x, y, bias=1).flat
    slope = ssxym / ssxm #sum((x-xmean)*(y-ymean)) / sum((x-xmean)**2)
    intercept = ymean - slope*xmean
    epsilon = factor - intercept - slope*size
    return epsilon

def timeit(func):
    @wraps(func)
    def t(*arg,**kwarg):
        t0=time.time()
        r=func(*arg,**kwarg)
        t1=time.time()
        print('Function: {} -- {} s'.format(func.__name__,t1-t0))
        return r
    return t