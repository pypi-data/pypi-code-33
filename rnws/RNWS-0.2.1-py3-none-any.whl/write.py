# -*- coding: utf-8 -*-
"""
Created on Thu May  3 17:51:39 2018

@author: yili.peng
"""

import os
import pandas as pd
from .timeit import timeit

@timeit
def write_df(df,path,file_pattern,**kwargs):
    '''
    dt*StkId
    '''
    if not os.path.exists(path):
        os.makedirs(path)
    for inx in df.index:
        df.loc[inx].to_csv(path+'\\'+file_pattern+'_'+str(inx)+'.csv',**kwargs)

@timeit
def write_dict(dictionary,path,file_pattern,**kwargs):
    if not os.path.exists(path):
        os.makedirs(path)
    for inx in dictionary.keys():
        dictionary[inx].to_csv(path+'\\'+file_pattern+'_'+str(inx)+'.csv',**kwargs)

@timeit
def write_factors(path,file_pattern,**kwargs):
    '''
    kwargs:{'f1':factor1,'f2':factor2,...}
    factor: dt*StkId
    '''
    result_DF=pd.DataFrame({(outerKey, innerKey): values for outerKey, innerDict in kwargs.items() for innerKey, values in innerDict.items()})
    if not os.path.exists(path):
        os.makedirs(path)
    for inx in result_DF.index:
        result_DF.loc[inx].unstack(level=0).rename_axis('StkID').to_csv(path+'\\'+file_pattern+'_'+str(inx)+'.csv',encoding='gbk')

@timeit
def write_dict_to_factors(path,file_pattern,**kwargs):
    if not os.path.exists(path):
        os.makedirs(path)
    for k,df in kwargs.items():
        df.to_csv(path+'\\{}_{}.csv'.format(file_pattern,k))
