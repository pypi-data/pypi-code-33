# -*- coding: utf-8 -*-
"""
Created on Thu May  3 17:21:35 2018

@author: yili.peng
"""

import pandas as pd
import os
import pkg_resources
from datetime import date
from glob import glob
from .timeit import timeit

class reading_data:
	trading_dt_path = pkg_resources.resource_filename('RNWS', 'data/trading_date.csv')
	trading_dt=pd.read_csv(trading_dt_path,header=None)[0]

def convert_type(dt):
    if type(dt) is int:
        return dt
    elif type(dt) is str:
        return int(dt)
    elif type(dt) in (date,pd.Timestamp):
        return int(dt.strftime('%Y%m%d'))
    else:
        raise Exception('Unidentified type of dt')

@timeit
def read_df(path,file_pattern,start=None,end=None,dt_range=None,inx_col=0,header=None,dat_col=1,**kwargs):
    '''
    if header is None, dat_col must be int
    otherwise dat_col shall be str or list
    '''
    if dt_range is None:
        dt_range=reading_data.trading_dt
    else:
        dt_range= pd.Series([convert_type(dt) for dt in dt_range])
            
    if (start is not None):
        dt_range=dt_range[int(start)<=dt_range]
    if (end is not None):
        dt_range=dt_range[int(end)>=dt_range]
    if (type(dat_col) is str) or (type(dat_col) is int):
        result=pd.DataFrame()
        for dt in dt_range.tolist():
            file=path+'\\'+file_pattern+'_'+str(dt)+'.csv'
            if os.path.exists(file):
                try:
                    r=pd.read_csv(file,header=header,index_col=inx_col,encoding='gbk',**kwargs)[dat_col].rename(dt)
                except UnicodeDecodeError:
                    r=pd.read_csv(file,header=header,index_col=inx_col,encoding='utf_8',**kwargs)[dat_col].rename(dt)
                result=result.append(r)
            else:
                pass
        return result.sort_index()
    elif (type(dat_col) is list) or (type(dat_col) is tuple):
        result=[pd.DataFrame() for i in range(len(dat_col))]
        for dt in dt_range.tolist():
            file=path+'\\'+file_pattern+'_'+str(dt)+'.csv'
            if os.path.exists(file):
                try:
                    r=pd.read_csv(file,header=header,index_col=inx_col,encoding='gbk',**kwargs)
                except UnicodeDecodeError:
                    r=pd.read_csv(file,header=header,index_col=inx_col,encoding='utf_8',**kwargs)
                for i in range(len(dat_col)):
                    result[i]=result[i].append(r[dat_col[i]].rename(dt))
            else:
                pass
        return [r.sort_index() for r in result]
    else:
        raise Exception('wrong dat_col type')
        
@timeit
def read_srs(path,file_pattern,start=None,end=None,dt_range=None,header=None,data_col=1,**kwargs):
    if dt_range is None:
        dt_range=reading_data.trading_dt
    else:
        dt_range= pd.Series([convert_type(dt) for dt in dt_range])
    if (start is not None):
        dt_range=dt_range[int(start)<=dt_range]
    if (end is not None):
        dt_range=dt_range[int(end)>=dt_range]
    result=pd.Series()
    for dt in dt_range.tolist():
        file=path+'\\'+file_pattern+'_'+str(dt)+'.csv'
        if os.path.exists(file):
            try:
                r=pd.read_csv(file,header=header,index_col=0,encoding='gbk',**kwargs)[data_col].tolist()
            except UnicodeDecodeError:
                r=pd.read_csv(file,header=header,index_col=0,encoding='utf_8',**kwargs)[data_col].tolist()
            result.at[dt]=r
        else:
            pass
    return result.sort_index()

@timeit	
def read_dict(path,file_pattern,start=None,end=None,dt_range=None,index_col=0,**kwargs):
    dt_range=reading_data.trading_dt
    if (start is not None):
        dt_range=dt_range[int(start)<=dt_range]
    if (end is not None):
        dt_range=dt_range[int(end)>=dt_range]
    result={}
    for dt in dt_range.tolist():
        file=path+'\\'+file_pattern+'_'+str(dt)+'.csv'
        if os.path.exists(file):
            try:
                r=pd.read_csv(file,index_col=index_col,encoding='gbk',**kwargs)
            except UnicodeDecodeError:
                r=pd.read_csv(file,index_col=index_col,encoding='utf_8',**kwargs)
            result[dt]=r.sort_index()
        else:
            pass
    return result

@timeit
def read_mdf(path,file_pattern,start=None,end=None,dt_range=None,inx_col=0,header=None,dat_col=None,**kwargs):
    '''
    columns are all factors if dat_col is None
    '''
    if dat_col is None:
        if dt_range is None:
            dt_range=reading_data.trading_dt
        else:
            dt_range= pd.Series([convert_type(dt) for dt in dt_range])
        if (start is not None):
            dt_range=dt_range[int(start)<=dt_range]
        if (end is not None):
            dt_range=dt_range[int(end)>=dt_range]
        file=path+'\\'+file_pattern+'_'+str(dt_range.tolist()[0])+'.csv'
        if os.path.exists(file):
            try:
                r=pd.read_csv(file,header=header,index_col=inx_col,encoding='gbk',**kwargs)
            except UnicodeDecodeError:
                r=pd.read_csv(file,header=header,index_col=inx_col,encoding='utf_8',**kwargs)
        dat_col=list(r.columns)
    result=read_df(path=path,file_pattern=file_pattern,start=start,end=end,inx_col=inx_col,header=header,dat_col=dat_col,**kwargs)
    return pd.concat(result,keys=dat_col).unstack(level=0).swaplevel(axis=1)

@timeit
def read_factors_to_dict(path,file_pattern):
    '''
    dataframes time * ticker
    '''
    lst=glob(path+'\\{}_*.csv'.format(file_pattern))
    d={}
    for l in lst:
        file_name=os.path.split(l)[1]        
        factor_name=file_name[(len(file_pattern)+1):-4]
        table=pd.read_csv(l,header=0,index_col=0)
        d.update({factor_name:table})
    return d