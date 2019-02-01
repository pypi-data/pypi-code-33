# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:04:39 2018

@author: yili.peng
"""


import numpy as np
import pandas as pd

class functions:
    '''
    df: dataframe / cap
    num: float
    both: dataframe or constant
    lg: logical df
    group: factorized dataframe
    cap: cap
    '''
    def _standardisation(df):
        return df.subtract(df.mean(axis=1),axis=0).divide(df.std(axis=1),axis=0)
    #return df
    def choose(lg,df1,df2):
        return functions._standardisation(df1.where(cond=lg.astype(bool),other=df2))
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
    def multiply_rank(df1,df2):
        return df1.rank(axis=1).multiply(df2.rank(axis=1))
    def rank(df):
        return df.rank(axis=1)
    def delay(df,num):
        d=int(np.ceil(abs(num)))
        return df.shift(d)
    def correlation(df1,df2,num):
        d=int(np.ceil(abs(num)))
        if d<2:
            d+=2
        r1=df1.rolling(d)
        r2=df2.rolling(d)
        return functions._standardisation(r1.corr(r2).replace(np.inf,np.nan).replace(-np.inf,np.nan))
    def covariance(df1,df2,num):
        d=int(np.ceil(abs(num)))
        if d<2:
            d+=2
        r1=df1.rolling(d)
        r2=df2.rolling(d)
        return functions._standardisation(r1.cov(r2))
    def scale(df):
        return functions._standardisation(df.divide(df.abs().sum(axis=1),axis=0))
    def delta(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.diff(d))
    def signedpower(df,num):
        if abs(num)>=3:
            num=3
        return functions._standardisation(df.pow(num))
    def linear_decay(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.rolling(d).apply(lambda x: np.average(x,weights=range(1,d+1))))
    def indneutralize(df,group):
        result=pd.DataFrame()
        tmp=pd.merge(left=df.stack().rename('df').reset_index(),right=group.stack().rename('group').reset_index(),\
                     on=['level_0','level_1'],how='outer').pivot(index='level_0',columns='level_1')
        for inx in tmp.index:
            df_tmp=tmp.loc[inx].unstack(level=0).infer_objects()
            df_mean=df_tmp.groupby('group').mean()
            s=df_tmp['df']-pd.Series(df_mean.reindex(df_tmp['group'])['df'].values,index=df_tmp.index)
            result=result.append(s.rename(inx))
        return functions._standardisation(result.reindex(df.index))
    def ts_min(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.rolling(d).min())
    def ts_max(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.rolling(d).max())
    def ts_argmax(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(np.argmax)
    def ts_argmin(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(np.argmin)
    def ts_rank(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(lambda x: x.argsort().argsort()[0])
    def ts_rank2(df,num):
        d=int(np.ceil(abs(num)))
        return df.rolling(d).apply(lambda x: x.argsort().argsort()[-1])
    def ts_sum(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.rolling(d).sum())
    def ts_product(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.rolling(d).apply(np.product))
    def ts_std(df,num):
        d=int(np.ceil(abs(num)))
        return functions._standardisation(df.rolling(d).std())
    def reg_cap(df,cap):
        S=pd.concat([df,cap],axis=1,keys=['df','cap'])
        r=pd.DataFrame(columns=df.columns)
        for inx in S.index:
            sample=S.loc[inx].unstack().dropna(axis=1)
            if sample.shape[1]<10:
                continue
            b=(sample.loc['cap'].mul(sample.loc['df']).sum())/(sample.loc['cap'].pow(2).sum())
            r=r.append(sample.loc['df'].sub(sample.loc['cap'].mul(b)).rename(inx))
        return functions._standardisation(r.reindex(df.index))
    #return logical lg (int 0/1)
    def le(df,both):
        return df.le(both).astype(float)
    def ge(df,both):
        return df.ge(both).astype(float)
    def or_df(lg,lg2):
        return (lg.astype(bool)|lg2.astype(bool)).astype(float)
    def eql(df,both):
        return df.eq(both).astype(float)