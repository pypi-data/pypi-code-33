# -*- coding: utf-8 -*-
"""
Created on Tue May  8 13:30:40 2018

@author: yili.peng
"""

import pandas as pd
#from copy import deepcopy
import numpy as np
from numba import jit
#from datetime import datetime

#def split_time(s):
#    '''
#    get date time from file names
#    '''
#    return list(filter(None,list(filter(None,s.split('.')))[0].split('_')))[-1]
#
#def pre_sus(x):
#    '''
#    for new stocks detection and recording
#    '''
#    y=deepcopy(x)
#    if x.isnull().any():
#        i=np.where(x.isnull())[0][-1]  
#        if i==0:
#            y.iloc[i:(i+20)]=1
#        y.fillna(1,inplace=True) 
#    return y

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

def seperate(l,n):
    k=len(l)
    if k==1:
        return pd.DataFrame([1.0]*n,columns=l,index=range(n))    
    weights_st=pd.DataFrame(seperate_core2(k,n),columns=l,index=range(n))
    return weights_st.div(weights_st.sum(axis=1),axis=0)
#
#def change_index(df,date_type='%Y%m%d'):
#    df1=df.copy()
#    try:        
#        df1.index=[datetime.strptime(str(t),date_type) for t in df1.index]
#    except:
#        print('index is not valid for strptime')        
#    return df1.rename_axis('dt').rename_axis('ticker',axis=1)
#
#@jit(nopython=True)
#def drawn_down(lst):
#    MIN=0
#    n=len(lst)
#    for i in range(n):
#        for j in range(i,n):
#            delta=lst[i]-lst[j]
#            if delta<MIN:
#                MIN=delta
#    return -MIN
#
#def apply_with_drawn_down(df):
#    r=pd.Series()
#    for k,g in df.items():
#        r.at[k]=drawn_down(g.tolist())
#    return r
#
#def monthmove(ym,delta=1):
#    y=int(ym)//100
#    m=int(ym)%100
#    ny=y+(m-1+delta)//12
#    nm=(m-1+delta)%12+1
#    return str(int(ny*100+nm))
#
#def check_time(dt1):
#    dt=dt1
#    while True:
#        try:
#            datetime.strptime(str(dt),'%Y%m%d')
#            break
#        except:
#            dt=int(dt)-1
#            if dt%100==0:
#                raise Exception('Wrong dt at check_time')
#    return datetime.strptime(str(dt),'%Y%m%d')

def portfolio_pct_change(pw,pw_new):
    return pw_new.sub(pw,fill_value=0).abs().sum()/2
