# -*- coding: utf-8 -*-
"""
Created on Tue May  8 13:30:40 2018

@author: yili.peng
"""

import pandas as pd
from copy import deepcopy
from numba import jit
import numpy as np
from datetime import datetime

def read_file(file,**kwag):
    '''
    read csv files with different encodings
    '''
    try:
        df=pd.read_csv(filepath_or_buffer=file,encoding='utf-8',**kwag)
    except UnicodeDecodeError:
        df=pd.read_csv(filepath_or_buffer=file,encoding='gbk',**kwag)
    return df

def seperate(l,n):
    '''
    calculate the weight of each element from l in n portfolios
    used in  back_test
    '''
    k=len(l)
    if k==1:
        return pd.DataFrame([1.0]*n,columns=l,index=range(n))
    shares=[1]*k
    weights=pd.DataFrame(0,columns=l,index=range(n))
    col=0
    row=0
    a=k/float(n)
    while row<n:
        a-=shares[col]
        if a>1e-5:
            weights.iloc[row,col]=shares[col]
            shares[col]=0
            col+=1
        else:
            weights.iloc[row,col]=shares[col]+a
            shares[col]=-a
            row+=1
            a=k/float(n)
    weights_st=weights/a
    return weights_st


@jit(nopython=True)
def seperate_core(k,n):
    a=k/float(n)
    b=1
    lst=[]
    lst2=[]
    for i in range(k+n-1):
        if b<=a:
            a-=b
            lst.append(b)
            b=1
        else:
            lst.append(a)
            b-=a
            a=k/float(n)
            lst2.append(i+1)
    return lst,lst2

@jit(nopython=True)
def seperate_core2(k,n):
    weights_st=np.zeros(shape=(n,k))
    lst,lst2=seperate_core(k,n)
    lst3=[0]+lst2+[len(lst)]
    l=0
    for i in range(n):
        for j in range(lst3[i],lst3[i+1]):
            weights_st[i,l]=lst[j]
            l+=1
        l-=1
    return weights_st

def seperate_new(l,n):
    k=len(l)
    if k==1:
        return pd.DataFrame([1.0]*n,columns=l,index=range(n))    
    weights_st=pd.DataFrame(seperate_core2(k,n),columns=l,index=range(n))
    return weights_st.div(weights_st.sum(axis=1),axis=0)

def change_index(df):
    df1=df.copy()
    df1.index=[datetime.strptime(str(t),'%Y%m%d') for t in df1.index]
    return df1.rename_axis('dt').rename_axis('ticker',axis=1)

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

def drawn_down(s):
    d=0
    for i in s.index:
        dd=s.loc[i:].min()/s.loc[:i].max()-1
        if dd<d:
            d=dd
    return -d

@jit(nopython=True)
def drawn_down_new(lst):
    MIN=0
    n=len(lst)
    for i in range(n):
        for j in range(i,n):
            delta=lst[i]-lst[j]
            if delta<MIN:
                MIN=delta
    return -MIN

def apply_with_drawn_down(df):
    r=pd.Series()
    for k,g in df.items():
        r.at[k]=drawn_down_new(g.tolist())
    return r


def portfolio_pct_change(pw,pw_new,double_sides_rate=0.003):
    return pw_new.sub(pw).abs().sum().mul(double_sides_rate/2)
