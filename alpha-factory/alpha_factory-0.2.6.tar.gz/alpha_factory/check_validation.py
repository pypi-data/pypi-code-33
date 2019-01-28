# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 15:33:46 2018

@author: yili.peng
"""
from .cprint import cprint,wrap_text
#import pandas as pd
import numpy as np
from numba import jit

def not_na(df,na_thresh=0.6,**kwarg):
    '''
    df: current generated df
    na_thresh: \u2208(0,1). Threshold of na portion. 
    '''
    if np.prod(df.shape)==0:
        cprint('\u2191\u2191\u2191'+wrap_text('is na')+'\u2191\u2191\u2191')
        return False
    na_pct=df.isna().sum().sum()/np.prod(df.shape)
    if na_pct>na_thresh:
        cprint('\u2191\u2191\u2191'+wrap_text('is na')+'\u2191\u2191\u2191')
        return False
    return True

def not_same(df,**kwarg):
    '''
    df: current generated df
    '''
    if df.max().max()==df.min().min():
        cprint('\u2191\u2191\u2191'+wrap_text('is same')+'\u2191\u2191\u2191')
        return False
    return True

#def not_duplicated(df,old_df_dict,cor_thresh=0.7,**kwarg):
#    '''
#    df: current generated df
#    old_df_dict: past generated df dictionary
#    cor_thresh: \u2208(0,1). Threshold to start random choice. Probability = (1-cor)I(cor>cor_thresh)/(1-cor_thresh) 
#    '''
#    for key,old_df in old_df_dict.items():
#        cor=pd.concat([df,old_df],keys=['new','old']).unstack().dropna(axis=1).T.corr().iloc[0,1]
#        if abs(cor) > cor_thresh:
#            cprint('\u2191\u2191\u2191'+wrap_text('is cor %s %.2f'%(key,cor))+'\u2191\u2191\u2191')
#            prob=abs((1-abs(cor))/(1-cor_thresh))
#            if np.random.choice([True,False],p=[prob,1-prob]):
#                pass
#            else:
#                return False
#    return True

@jit(nopython=True)
def corr(t1v,t2v):
    flag=(~np.isnan(t1v))& (~np.isnan(t2v))
    t1v_tmp=t1v[flag]
    t2v_tmp=t2v[flag]
    n=len(t1v_tmp)
    t1m=np.sum(t1v_tmp)/n
    t2m=np.sum(t2v_tmp)/n
    return np.sum(((t1v_tmp-t1m)/np.std(t1v_tmp))*((t2v_tmp-t2m)/np.std(t2v_tmp)))/n

def get_abs_corr(t1,t2):
    col=list(set(t1.columns)&set(t2.columns))
    t1_tmp=t1[col].unstack()
    t2_tmp=t2[col].reindex(t1.index).unstack()
    t1v=t1_tmp.values.reshape(-1)
    t2v=t2_tmp.values.reshape(-1)
    return abs(corr(t1v,t2v))

def not_duplicated2(df,old_df_dict,cor_thresh=0.7,**kwarg):
    '''
    df: current generated df
    old_df_dict: past generated df dictionary
    cor_thresh: \u2208(0,1). Threshold to start random choice. Probability = (1-cor)I(cor>cor_thresh)/(1-cor_thresh) 
    '''
    for key,old_df in old_df_dict.items():
#        cor=pd.concat([df,old_df],keys=['new','old']).unstack().dropna(axis=1).T.corr().iloc[0,1]
        abs_cor=get_abs_corr(df,old_df)
        if abs_cor > cor_thresh:
            cprint('\u2191\u2191\u2191'+wrap_text('is cor %s %.2f'%(key,abs_cor))+'\u2191\u2191\u2191')
            prob=abs((1-abs_cor)/(1-cor_thresh))
            if np.random.choice([True,False],p=[prob,1-prob]):
                pass
            else:
                return False
    return True

def is_validate(df,old_df_dict,**kwarg):
    if not not_na(df,**kwarg):
        return False
    elif not not_same(df,**kwarg):
        return False
    elif not not_duplicated2(df,old_df_dict,**kwarg):
        return False
    else:
        return True

#df=pd.DataFrame(np.random.random(size=(1000,3000)))
#old_df_dict={'t1':pd.DataFrame(np.random.random(size=(1000,3000))),
#             't2':pd.DataFrame(np.random.random(size=(1000,3000))),
#             't3':pd.DataFrame(np.random.random(size=(1000,3000))),
#             't4':pd.DataFrame(np.random.random(size=(1000,3000))),
#             't5':pd.DataFrame(np.random.random(size=(1000,3000)))}
#%timeit not_duplicated(df,old_df_dict)#4.68 s
#%timeit not_duplicated2(df,old_df_dict)#1.09 s
