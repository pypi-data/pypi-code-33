# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 10:44:00 2019

@author: yili.peng
"""

import numpy as np
import pandas as pd
from numba import njit,prange
from functools import wraps

def _check_same_shape(func):
    @wraps(func)
    def check(*args,**kwargs):
        l1=[i for i in args if isinstance(i,pd.DataFrame)]
        l2=[i for i in kwargs.values() if isinstance(i,pd.DataFrame)]
        l=l1+l2
        if len(l)>=1:
            common_inx=l[0].index
            common_col=l[0].columns
            for j in l[1:]:
                assert common_inx.equals(j.index),'index not same'
                assert common_col.equals(j.columns),'columns not same'
        return pd.DataFrame(func(*args,**kwargs),index=common_inx,columns=common_col)
    return check

# to speedup computing

@njit(parallel=True)
def _standardisation_withnumba(x):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        sub=x[i]        
        sub2=sub[~np.isnan(sub)]
        n2=len(sub2)
        if n2 <=1:
            for j in prange(m):
                r[i,j]=np.nan
        else:
            mu=np.sum(sub2)/n2
            var=0
            for k in prange(n2):
                var+= (sub2[k] - mu ) **2
            sigma=np.sqrt(var/(n2-1))
            
            for j in prange(m):
                if np.isnan(sub[j]):
                    r[i,j]=np.nan
                else:
                    r[i,j]=(sub[j]-mu)/sigma
    return r

@njit(parallel=True)
def _choose_withnumba(l,x,y):
    n,m=l.shape
    r=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if l[i,j] == 1:
                r[i,j] = x[i,j]
            else:
                r[i,j] = y[i,j]
    return r

#@njit(parallel=True,fastmath=True)
#def _rank_withnumba(x):
#    n,m=x.shape
#    r=np.empty((n,m))
#    for i in prange(n):
#        s=np.argsort(x[i])
#        for j in prange(m):
#            r[i,s[j]]=j
#    return r

@njit(parallel=True)
def _corr_withnumba(x,y):
    f=~(np.isnan(x) | np.isnan(y))
    sub_x=x[f]
    sub_y=y[f]
    n2=len(sub_x)
    if n2 <=1:
        return np.nan
    else:
        mu_x=np.sum(sub_x)/n2
        mu_y=np.sum(sub_y)/n2
        var_x=0
        var_y=0
        var_xy=0
        for k in prange(n2):
            var_x+= (sub_x[k] - mu_x) **2
            var_y+= (sub_y[k] - mu_y) **2
            var_xy+= (sub_x[k] - mu_x) * (sub_y[k] - mu_y)
    bot=np.sqrt(var_x*var_y)
    if bot<1e-3:
        return np.nan
    else:
        return var_xy/bot
    
@njit(parallel=True)
def _std_withnumba(x):
    f=~(np.isnan(x))
    sub_x=x[f]
    n2=len(sub_x)
    if n2 <=1:
        return np.nan
    else:
        mu_x=np.sum(sub_x)/n2
        var_xx=0
        for k in prange(n2):
            var_xx += (sub_x[k] - mu_x) **2
    return np.sqrt(var_xx/(n2-1))

@njit(parallel=True)
def _cov_withnumba(x,y):
    f=~(np.isnan(x) | np.isnan(y))
    sub_x=x[f]
    sub_y=y[f]
    n2=len(sub_x)
    if n2 <=1:
        return np.nan
    else:
        mu_x=np.sum(sub_x)/n2
        mu_y=np.sum(sub_y)/n2
        var_xy=0
        for k in prange(n2):
            var_xy+= (sub_x[k] - mu_x) * (sub_y[k] - mu_y)
    return var_xy/(n2-1)

@njit(parallel=True)
def _rolling_cov_withnumba(x,y,a):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        if i < a-1:
            for j in prange(m):
                r[i,j]=np.nan
        else:
            for j in prange(m):
                sub1=x[i-a+1:i+1,j]
                sub2=y[i-a+1:i+1,j]
                r[i,j]=_cov_withnumba(sub1,sub2)
    return r

@njit(parallel=True)
def _rolling_corr_withnumba(x,y,a):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        if i < a-1:
            for j in prange(m):
                r[i,j]=np.nan
        else:
            for j in prange(m):
                sub1=x[i-a+1:i+1,j]
                sub2=y[i-a+1:i+1,j]
                r[i,j]=_corr_withnumba(sub1,sub2)
    return r

@njit(parallel=True)
def _linear_decay_withnumba(x,a):
    n,m=x.shape
    r=np.empty((n,m))    
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            b=len(sub_sample)
            v=0
            s=0
            for l in prange(a):
                if l>=b:
                    continue
                elif np.isnan(sub_sample[b-l-1]):
                    continue
                else: 
                    v+=sub_sample[b-l-1]*(a-l)
                    s+=(a-l)
            if s>0:
                r[i,j]=v/s
            else:
                r[i,j]=np.nan
    return r

@njit(parallel=True)
def _sqr_decay_withnumba(x,a):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            b=len(sub_sample)
            v=0
            s=0
            for l in prange(a):
                if l>=b:
                    continue
                elif np.isnan(sub_sample[b-l-1]):
                    continue
                else: 
                    v+=sub_sample[b-l-1]*((a-l)**2)
                    s+=((a-l)**2)
            if s>0:
                r[i,j]=v/s
            else:
                r[i,j]=np.nan
    return r

@njit(parallel=True)
def _rolling_max_withnumba(x,a):
    n,m=x.shape
    r1=np.empty((n,m))
    r2=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            b=len(sub_sample)
            mx=-999
            amx=0
            for l in prange(a):
                if l>=b:
                    continue
                elif np.isnan(sub_sample[b-l-1]):
                    continue
                else:
                    if sub_sample[b-l-1]>mx:
                        mx=sub_sample[b-l-1]
                        amx=l
            if mx==-999:
                mx=np.nan
                amx=np.nan
            r1[i,j] = mx
            r2[i,j] = amx
    return r1,r2

@njit(parallel=True)
def _rolling_min_withnumba(x,a):
    n,m=x.shape
    r1=np.empty((n,m))
    r2=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            b=len(sub_sample)
            mn=999
            amn=0
            for l in prange(a):
                if l>=b:
                    continue
                elif np.isnan(sub_sample[b-l-1]):
                    continue
                else:
                    if sub_sample[b-l-1]<mn:
                        mn=sub_sample[b-l-1]
                        amn=l
            if mn==999:
                mn=np.nan
                amn=np.nan
            r1[i,j] = mn
            r2[i,j] = amn
    return r1,r2

@njit(parallel=True)
def _rolling_avg_withnumba(x,a):
    n,m=x.shape
    r1=np.empty((n,m))
    r2=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            b=len(sub_sample)
            mn=999
            amn=0
            for l in prange(a):
                if l>=b:
                    continue
                elif np.isnan(sub_sample[b-l-1]):
                    continue
                else:
                    if sub_sample[b-l-1]<mn:
                        mn=sub_sample[b-l-1]
                        amn=l
            if mn==999:
                mn=np.nan
                amn=np.nan
            r1[i,j] = mn
            r2[i,j] = amn
    return r1,r2

@njit
def _rank_last_score(a):
    if np.isnan(a[-1]):
        return np.nan
    else:
        b=a[~np.isnan(a)]
        n=len(b)
        ranks=np.empty_like(b)
        s=np.argsort(b)
        ranks[s] = np.arange(n)/n
        return ranks[-1]

@njit
def _rank_first_score(a):
    if np.isnan(a[0]):
        return np.nan
    else:
        b=a[~np.isnan(a)]
        n=len(b)
        ranks=np.empty_like(b)
        s=np.argsort(b)
        ranks[s] = np.arange(n)/n
        return ranks[0]


@njit(parallel=True)
def _rolling_rank_last_withnumba(x,a):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            r[i,j]=_rank_last_score(sub_sample)
    return r

@njit(parallel=True)
def _rolling_rank_first_withnumba(x,a):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            r[i,j]=_rank_first_score(sub_sample)
    return r

@njit(parallel=True)
def _avgnan(x):
    n=len(x)
    s=0
    c=0
    for i in prange(n):
       if np.isnan(x[i]):
           continue
       else:
           s+=x[i]
           c+=1
    if c<1e-3:
        return np.nan
    else:
        return s/c

@njit(parallel=True)
def _rolling_sum_withnumba(x,a):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            avg=_avgnan(sub_sample)
            r[i,j]=avg*a
    return r

@njit(parallel=True)
def _rolling_std_withnumba(x,a):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub_sample=x[0:i+1,j]
            else:
                sub_sample=x[i-a+1:i+1,j]
            std=_std_withnumba(sub_sample)
            r[i,j]=std
    return r

@njit(parallel=True)
def _easy_regression_withnumba(x,y):
    f=~(np.isnan(x) | np.isnan(y))
    sub_x=x[f]
    sub_y=y[f]
    n=len(x)
    n2=len(sub_x)    
    res=np.empty(n)
    if n2 <=1:
        for i in prange(n):
            res[i]=np.nan
    else:
        mu_x=np.sum(sub_x)/n2
        mu_y=np.sum(sub_y)/n2
        var_x=0
#        var_y=0
        var_xy=0
        for k in prange(n2):
            var_x+= (sub_x[k] - mu_x) **2
#            var_y+= (sub_y[k] - mu_y) **2
            var_xy+= (sub_x[k] - mu_x) * (sub_y[k] - mu_y)
        if var_x == 0:
            for i in prange(n):
                res[i] = np.nan
        else:
            slope = var_xy/var_x
            intercept = mu_y - slope * mu_x
            for i in prange(n):
                res[i] = y[i] - intercept - slope*x[i]
    return res

@njit(parallel=True)
def _easy_beta_withnumba(x,y):
    f=~(np.isnan(x) | np.isnan(y))
    sub_x=x[f]
    sub_y=y[f]
    n2=len(sub_x)
    if n2 <=1:
        slope=np.nan
    else:
        mu_x=np.sum(sub_x)/n2
        mu_y=np.sum(sub_y)/n2
        var_x=0
        var_xy=0
        for k in prange(n2):
            var_x+= (sub_x[k] - mu_x) **2
            var_xy+= (sub_x[k] - mu_x) * (sub_y[k] - mu_y)
        if var_x==0:
            slope=np.nan
        else:
            slope = var_xy/var_x
    return slope

@njit(parallel=True)
def _rolling_beta_withnumba(x,y,a):
    n,m=x.shape
    r=np.empty((n,m))
    for i in prange(n):
        for j in prange(m):
            if i < a-1:
                sub1=x[0:i+1,j]
                sub2=y[0:i+1,j]
            else:
                sub1=x[i-a+1:i+1,j]
                sub2=y[i-a+1:i+1,j]
            r[i,j]=_easy_beta_withnumba(sub1,sub2)
    return r    

class functions:
    '''
    df: dataframe / cap
    num: float
    both: dataframe or constant
    lg: logical df
    group: factorized dataframe
    cap: cap
    '''
    @_check_same_shape
    def _standardisation(df):        
        return _standardisation_withnumba(df.values)
    #return df
    @_check_same_shape
    def choose(lg,df1,df2):
        return _standardisation_withnumba(_choose_withnumba(lg.values,df1.values,df2.values))
    
    def absolute(df):
        return functions._standardisation(df.abs())
    
    def log(df):
        return functions._standardisation(np.log(df.abs()+1))
    
    def sign(df):
        return np.sign(df)
    
    def add(df,both):
        return functions._standardisation(df.add(both))
    
    def subtract(df,both):
        return functions._standardisation(df.subtract(both))
    
    def multiply(df,both):
        return functions._standardisation(df.multiply(both))
    
    def divide(df,both):
        if (type(both) in (float,int)) and both==0:
            return functions._standardisation(df)
        elif type(both) == pd.DataFrame:
            both=both.replace(0,np.nan)
        return functions._standardisation(df.divide(both))    

    def multiply_rank(df1,df2):# XXX slow
        return df1.rank(axis=1).multiply(df2.rank(axis=1))   
   
    def rank(df):# XXX slow
        return df.rank(axis=1)
    
    def delay(df,num):
        d=int(np.ceil(abs(num)))
        return df.shift(d)
    @_check_same_shape
    def correlation(df1,df2,num):
        d=int(np.ceil(abs(num)))
        if d<2:
            d+=2
        return _standardisation_withnumba(_rolling_corr_withnumba(df1.values,df2.values,d))  
    @_check_same_shape
    def correlation10(df1,df2,num):
        d=int(np.ceil(abs(num)))*10
        
        if d<2:
            d+=2
        return _standardisation_withnumba(_rolling_corr_withnumba(df1.values,df2.values,d)) 
    @_check_same_shape
    def covariance(df1,df2,num):
        d=int(np.ceil(abs(num)))
        if d<2:
            d+=2
        return _standardisation_withnumba(_rolling_cov_withnumba(df1.values,df2.values,d))
    @_check_same_shape
    def covariance10(df1,df2,num):
        d=int(np.ceil(abs(num)))*10
        if d<2:
            d+=2
        return _standardisation_withnumba(_rolling_cov_withnumba(df1.values,df2.values,d))
    def scale(df):
        return df.divide(df.abs().sum(axis=1),axis=0)
    
    def delta(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.diff(d))
    
    def pct_change(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.pct_change(d))
    
    def signedpower(df,num):
        if abs(num)>=3:
            num=3
        return functions._standardisation(df.pow(num))
    @_check_same_shape
    def linear_decay(df,num):
        d=int(np.ceil(abs(num)))
        return _standardisation_withnumba(_linear_decay_withnumba(df.values,d))
    @_check_same_shape
    def linear_decay10(df,num):
        d=int(np.ceil(abs(num)))*10
        return _standardisation_withnumba(_linear_decay_withnumba(df.values,d))
    @_check_same_shape
    def sqr_decay(df,num):
        d=int(np.ceil(abs(num)))
        return _standardisation_withnumba(_sqr_decay_withnumba(df.values,d))
    @_check_same_shape
    def sqr_decay10(df,num):
        d=int(np.ceil(abs(num)))*10
        return _standardisation_withnumba(_sqr_decay_withnumba(df.values,d)) 
    @_check_same_shape
    def indneutralize(df,group):# XXX slow
        l=[]
        for inx in df.index:
            df_tmp=pd.DataFrame([df.loc[inx].values,group.loc[inx].values],columns=df.columns,index=['df','group']).T.infer_objects()
            l.append((df_tmp.df-df_tmp.groupby('group').df.transform(np.mean)).values)
        return _standardisation_withnumba(np.array(l))
    @_check_same_shape
    def ts_min(df,num):
        d=int(np.ceil(abs(num)))
        mn,amn=_rolling_min_withnumba(df.values,d)
        return _standardisation_withnumba(mn)
    @_check_same_shape
    def ts_min10(df,num):
        d=int(np.ceil(abs(num)))*10
        mn,amn=_rolling_min_withnumba(df.values,d)
        return _standardisation_withnumba(mn)
    @_check_same_shape
    def ts_argmin(df,num):
        d=int(np.ceil(abs(num)))
        mn,amn=_rolling_min_withnumba(df.values,d)
        return _standardisation_withnumba(amn)
    @_check_same_shape
    def ts_argmin10(df,num):
        d=int(np.ceil(abs(num)))*10
        mn,amn=_rolling_min_withnumba(df.values,d)
        return _standardisation_withnumba(amn)
    @_check_same_shape
    def ts_max(df,num):
        d=int(np.ceil(abs(num)))
        mx,amx=_rolling_max_withnumba(df.values,d)
        return _standardisation_withnumba(mx)
    @_check_same_shape
    def ts_max10(df,num):
        d=int(np.ceil(abs(num)))*10
        mx,amx=_rolling_max_withnumba(df.values,d)
        return _standardisation_withnumba(mx)
    @_check_same_shape
    def ts_argmax(df,num):
        d=int(np.ceil(abs(num)))
        mx,amx=_rolling_max_withnumba(df.values,d)
        return _standardisation_withnumba(amx)
    @_check_same_shape
    def ts_argmax10(df,num):
        d=int(np.ceil(abs(num)))*10
        mx,amx=_rolling_max_withnumba(df.values,d)
        return _standardisation_withnumba(amx)
    @_check_same_shape
    def ts_rank_first(df,num):
        d=int(np.ceil(abs(num)))
        return _standardisation_withnumba(_rolling_rank_first_withnumba(df.values,d))
    @_check_same_shape
    def ts_rank_first10(df,num):
        d=int(np.ceil(abs(num)))*10
        return _standardisation_withnumba(_rolling_rank_first_withnumba(df.values,d))
    @_check_same_shape
    def ts_rank_last(df,num): # XXX slow
        d=int(np.ceil(abs(num)))
        return _standardisation_withnumba(_rolling_rank_last_withnumba(df.values,d))
    @_check_same_shape
    def ts_rank_last10(df,num): # XXX slow
        d=int(np.ceil(abs(num)))*10
        return _standardisation_withnumba(_rolling_rank_last_withnumba(df.values,d))    
    @_check_same_shape
    def ts_sum(df,num):
        d=int(np.ceil(abs(num)))
        return _standardisation_withnumba(_rolling_sum_withnumba(df.values,d))
    @_check_same_shape
    def ts_sum10(df,num):
        d=int(np.ceil(abs(num)))*10
        return _standardisation_withnumba(_rolling_sum_withnumba(df.values,d))
    
#    def ts_product(df,num):
#        d=int(np.ceil(abs(num)))
#        return functions._standardisation(df.rolling(d).apply(np.product))
#    def ts_product10(df,num):
#        d=int(np.ceil(abs(num)))*10
#        return functions._standardisation(df.rolling(d).apply(np.product))
#   
    def ts_std(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.rolling(d).std())
    
    def ts_std10(df,num):
        d=int(np.ceil(abs(num)))*10
        return functions._standardisation(df.rolling(d).std())
    
    @_check_same_shape
    def reg_beta10(df1,df2,num):
        d=int(np.ceil(abs(num)))*10
        return _standardisation_withnumba(_rolling_beta_withnumba(df1.values,df2.values,d))
    
    @_check_same_shape
    def reg_cap(df,cap):
        l=[]
        for inx in df.index:
            res=_easy_regression_withnumba(cap.loc[inx].values,df.loc[inx].values)            
            l.append(res)
        return _standardisation_withnumba(np.array(l))        
    
    def diff_change(df,num):
        d=int(np.ceil(abs(num)))
        df1=df.shift(d)
        return functions._standardisation((df-df1)/(df+df1))

    #return logical lg (int 0/1)
    def le(df,both):
        return df.le(both).astype(float)
    def ge(df,both):
        return df.ge(both).astype(float)
    def or_df(lg,lg2):
        return (lg.astype(bool)|lg2.astype(bool)).astype(float)
    def eql(df,both):
        return df.eq(both).astype(float)