# -*- coding: utf-8 -*-
"""
Created on Mon May 14 15:52:13 2018

@author: yili.peng
"""
import pandas as pd
from copy import deepcopy
import numpy as np
from datetime import datetime
import warnings
from glob import glob
from multiprocessing import Pool
from joblib import Parallel,delayed
import time as tm
import os
import seaborn as sns
import matplotlib.pyplot as plt
from .global_func import read_file
#from .global_func import drawn_down
from .global_func import apply_with_drawn_down,drawn_down_new
def bts_mul(X):
    '''
    for back_test_summary
    '''
    factor,Backtest=X[0],X[1]#,reference_flag,reference_df,renewal_date #,X[2],X[3],X[4]
    one_year=250
    portfolio_info=pd.DataFrame()
    portfolio=deepcopy(Backtest[factor])
    portfolio_info['annual_return']=portfolio.apply(lambda x: (x.iloc[-1]/x.iloc[0])**(one_year/len(x))-1 if len(x)>0 else np.nan)              
    portfolio_info['annual_volatility']=portfolio.apply(lambda x: x.pct_change().dropna().std()*(one_year)**0.5)
    portfolio_info['sharpe_ratio']=portfolio.apply(lambda x: (x.pct_change().dropna().mean()-0.03)/x.pct_change().dropna().std()*((one_year)**0.5) if x.pct_change().dropna().std()>0 else np.nan) ##### # risk free rate=0.03, annually
    portfolio_info['draw_down']=apply_with_drawn_down(portfolio) #portfolio.apply(drawn_down)
    portfolio_info['rank']=portfolio_info['annual_return'].rank(ascending=False)

    long_short_info=pd.Series(name='long_short')
    high=portfolio.iloc[:,0].pct_change().fillna(0)
    inx_high=portfolio.columns[0]
    low=portfolio.iloc[:,-1].pct_change().fillna(0)
    inx_low=portfolio.columns[-1]
    long_short=high-low 
    long_short_annual_return_tmp=(np.prod(long_short+1)**(one_year/len(long_short))-1 if len(long_short)>0 else np.nan)
    if long_short_annual_return_tmp is not np.nan:
        if long_short_annual_return_tmp<0:
            long_short*=-1
            long_short_annual_return_tmp=np.prod(long_short+1)**(one_year/len(long_short))-1 
            high,low=low,high
            inx_high,inx_low=inx_low,inx_high
    long_short_info['annual_return']=long_short_annual_return_tmp
    long_short_info['annual_volatility']=long_short.std()*((one_year)**0.5)
    long_short_info['sharpe_ratio']=((long_short.mean()-0.03)/long_short.std()*((one_year)**0.5) if long_short.std()>0 else np.nan)
    long_short_info['draw_down']=drawn_down_new((long_short+1).cumprod().tolist())  #drawn_down((long_short+1).cumprod()) 
    long_short_info_df=pd.DataFrame([long_short_info])
    
    ref_info=pd.DataFrame()
#    if reference_flag is True:
#        ref=reference_df.loc[portfolio.index,].dropna(axis=0)
#        ref_info['annual_return']=ref.apply(lambda x: (x.iloc[-1]/x.iloc[0])**(one_year/len(x))-1 if len(x)>0 else np.nan) 
#        ref_info['annual_volatility']=ref.apply(lambda x: x.pct_change().dropna().std()*(one_year)**0.5)  
#        ref_info['sharpe_ratio']=ref.apply(lambda x: x.pct_change().dropna().mean()/x.pct_change().dropna().std()*(one_year)**0.5 if x.pct_change().dropna().std()>0 else np.nan)# risk free rate=0, annually
#        ref_info['draw_down']=apply_with_drawn_down(ref) #ref.apply(drawn_down)                      
    
#    if renewal_date is None:                
    monthly=pd.Series(portfolio.index,index=portfolio.index).map(lambda x: (x.year,x.month))                
#    else:
#        group=pd.Series(0,index=portfolio.index)
#        time_p=portfolio.index[0]
#        time_0=time_p+pd.tseries.offsets.DateOffset(months=1)
#        time_q=datetime(year=time_0.year,month=time_0.month,day=renewal_date)
#        while (group.index>time_q).any():
#            group[group.index>time_q]+=1
#            time_q+=pd.tseries.offsets.DateOffset(months=1)
#        monthly=group.map(group.reset_index().groupby(0).apply(lambda x: x['index'].iloc[0].strftime('%Y-%m-%d')).to_dict())
#   
    portfolio['Month']=monthly
    return_monthly=portfolio.groupby('Month').aggregate(lambda x: x.iloc[-1]/x.iloc[0]-1).T
    average_rank=return_monthly.apply(lambda x: x.rank(ascending=False),axis=0).apply(np.mean,axis=1)
    return_monthly['Average_rank']=average_rank
    
    long_short_0=pd.concat([long_short,monthly],axis=1).rename(columns={0:'Winning_rate',1:'Month'})
    win_rate_by_month=long_short_0.groupby('Month').aggregate(lambda x: np.mean(x>0)).T           

    high_0=pd.concat([high,monthly],axis=1).rename(columns=lambda x: 'Winning_rate' if x !=0 else 'Month')
    low_0=pd.concat([low,monthly],axis=1).rename(columns=lambda x: 'Winning_rate' if x !=0 else 'Month')
    win_rate_daily=(long_short>0).mean()
    win_rate_monthly=np.mean((high_0.groupby('Month').aggregate(lambda x: np.prod(x+1)-1).values-low_0.groupby('Month').aggregate(lambda x: np.prod(x+1)-1).values)>0)
    win_rate_by_month['Daily']=win_rate_daily
    win_rate_by_month['Monthly']=win_rate_monthly   

    port_best=portfolio_info.sort_values(by='annual_return',ascending=False).iloc[0,:]
    port_best=pd.concat([port_best,long_short_info.rename(lambda x: 'long_short_'+x)]).rename(factor)
    port_best['long_short_win_ratio_monthly']=win_rate_monthly  
    port_best['long_short_win_ratio_daily']=win_rate_daily
    port_best['order']='>'.join(portfolio_info.sort_values('rank').index)
    port_best['long_short_order']=inx_high+'-'+inx_low
    port_best['start_time']=datetime.strftime(portfolio.index[0],'%Y%m%d')
    port_best['end_time']=datetime.strftime(portfolio.index[-1],'%Y%m%d')
    Dict1={factor:pd.concat([portfolio_info,long_short_info_df,ref_info],axis=0)}
    Table2=port_best
    Dict3={factor:pd.concat([return_monthly,win_rate_by_month],axis=0)}
    return Dict1,Table2,Dict3
     
def back_test_summary(Backtest,processors=None,back_end='loky',**kwarg):#reference_path=None,reference_flag=False,renewal_date=None,
    '''        
    summarize backtest result w/ multiprocessing
    
    reference_flag: logic, whether to compare reference index
    reference_path: path to store reference. filname index.csv,header=None
    renewal_date: monthly reneal date. Set as None if daily renewal
    back_end: 'loky' (default) or 'multiprocess'
    '''
    t0=tm.time()
    print('\r\tBack Test Summary \t          start          ')
    warnings.simplefilter(action = "ignore", category = RuntimeWarning)  
#    reference_flag=(reference_flag if reference_path is not None else False)
#    reference_df=pd.DataFrame()
#    if reference_flag is True:
#
#        for file_name in glob(reference_path+'\*.csv'):          
#            reference_name=file_name.split('\\')[-1].split('.')[0]
#            reference=read_file(file_name,header=None)
#            reference.iloc[:,0]=reference.iloc[:,0].map(lambda x : datetime.strptime(x,'%Y-%m-%d'))
#            reference=reference.set_index(0)[2].rename(reference_name)
#            reference_df[reference_name]=reference
#    
    Dict1={}
    Table2=pd.DataFrame()
    Dict3={}
    
    X=[]
    for factor in Backtest.keys():
        X.append([factor,Backtest]) #,reference_flag,reference_df,renewal_date   
    if back_end=='loky':
         multi_res=Parallel(n_jobs=processors)(delayed(bts_mul)(x) for x in X)
    elif back_end=='multiprocess':
        pool = Pool(processes=processors)
        multi_res=pool.map(bts_mul, X)
        pool.close()
        pool.join()
    else :
        raise Exception('Back_end not support. Use loky or multiprocess')
    for res in multi_res:
         Dict1.update(res[0])   
         Table2=Table2.append(res[1])
         Dict3.update(res[2])
    Table2=Table2.drop('rank',axis=1)
    t1=tm.time()
    print('\r\tBack Test Summary \t          finished          ')
    print('total time: %.3f s'%(t1-t0))
    return Dict1,Table2,Dict3
#
#def back_test_summary3(Backtest,reference_flag=False,reference_path=None,renewal_date=None,**kwarg):
#    '''        
#    summarize backtest result w/o multiprocessing
#    
#    reference_flag: logic, whether to compare reference index
#    reference_path: path to store reference.  reference 
#    renewal_date: monthly reneal date. Set as None if daily renewal
#    '''
#    t0=tm.time()
#    print('\r\tBack Test Summary \t          start          ')
#    warnings.simplefilter(action = "ignore", category = RuntimeWarning)
#    reference_flag=(reference_flag if reference_path is not None else False)
#    reference_df=pd.DataFrame()
#    if reference_flag:
#
#        for file_name in glob(reference_path+'\*.csv'):          
#            reference_name=file_name.split('\\')[-1].split('.')[0]
#            reference=read_file(file_name,header=None)
#            reference.iloc[:,0]=reference.iloc[:,0].map(lambda x : datetime.strptime(x,'%Y-%m-%d'))
#            reference=reference.set_index(0)[2].rename(reference_name)
#            reference_df[reference_name]=reference
#    
#    Dict1={}
#    Table2=pd.DataFrame()
#    Dict3={}
#    one_year=250
#    fac_counts=1
#    fac_len=len(Backtest)
#    for factor in Backtest.keys():
#        print('\r\tBack Test Summary \t step %d/%d  %s'%(fac_counts,fac_len,factor),end='\r')
#        fac_counts+=1
#        portfolio_info=pd.DataFrame()
#        portfolio=deepcopy(Backtest[factor])
#        portfolio_info['annual_return']=portfolio.apply(lambda x: (x.iloc[-1]/x.iloc[0])**(one_year/len(x))-1 if len(x)>0 else np.nan)              
#        portfolio_info['annual_volatility']=portfolio.apply(lambda x: x.pct_change().dropna().std()*(one_year)**0.5)
#        portfolio_info['sharpe_ratio']=portfolio.apply(lambda x: x.pct_change().dropna().mean()/x.pct_change().dropna().std()*((one_year)**0.5) if x.pct_change().dropna().std()>0 else np.nan) ##### # risk free rate=0, annually
#        portfolio_info['draw_down']=portfolio.apply(drawn_down)
#        portfolio_info['rank']=portfolio_info['annual_return'].rank(ascending=False)
#
#        long_short_info=pd.Series(name='long_short')
#        high=portfolio.iloc[:,0].pct_change().fillna(0)
#        inx_high=portfolio.columns[0]
#        low=portfolio.iloc[:,-1].pct_change().fillna(0)
#        inx_low=portfolio.columns[-1]
#        long_short=high-low 
#        long_short_annual_return_tmp=(np.prod(long_short+1)**(one_year/len(long_short))-1 if len(long_short)>0 else np.nan)
#        if long_short_annual_return_tmp is not np.nan:
#            if long_short_annual_return_tmp<0: #判断多空
#                long_short*=-1
#                long_short_annual_return_tmp=np.prod(long_short+1)**(one_year/len(long_short))-1 
#                high,low=low,high
#                inx_high,inx_low=inx_low,inx_high
#        long_short_info['annual_return']=long_short_annual_return_tmp
#        long_short_info['annual_volatility']=long_short.std()*((one_year)**0.5)
#        long_short_info['sharpe_ratio']=(long_short.mean()/long_short.std()*((one_year)**0.5) if long_short.std()>0 else np.nan)
#        long_short_info['draw_down']=drawn_down((long_short+1).cumprod()) 
#        long_short_info_df=pd.DataFrame([long_short_info])
#        
#        ref_info=pd.DataFrame()
#        if reference_flag is True:
#            ref=reference_df.loc[portfolio.index,].dropna(axis=0)
#            ref_info['annual_return']=ref.apply(lambda x: (x.iloc[-1]/x.iloc[0])**(one_year/len(x))-1 if len(x)>0 else np.nan) 
#            ref_info['annual_volatility']=ref.apply(lambda x: x.pct_change().dropna().std()*(one_year)**0.5)  
#            ref_info['sharpe_ratio']=ref.apply(lambda x: x.pct_change().dropna().mean()/x.pct_change().dropna().std()*(one_year)**0.5 if x.pct_change().dropna().std()>0 else np.nan)# risk free rate=0, annually
#            ref_info['draw_down']=ref.apply(drawn_down) 
#            
#        Dict1[factor]=pd.concat([portfolio_info,long_short_info_df,ref_info],axis=0)
#                 
#        
#        if renewal_date is None:                
#            monthly=pd.Series(portfolio.index,index=portfolio.index).map(lambda x: (x.year,x.month))                
#        else:
#            group=pd.Series(0,index=portfolio.index)
#            time_p=portfolio.index[0]
#            time_0=time_p+pd.tseries.offsets.DateOffset(months=1)
#            time_q=datetime(year=time_0.year,month=time_0.month,day=renewal_date)
#            while (group.index>time_q).any():
#                group[group.index>time_q]+=1
#                time_q+=pd.tseries.offsets.DateOffset(months=1)
#            monthly=group.map(group.reset_index().groupby(0).apply(lambda x: x['index'].iloc[0].strftime('%Y-%m-%d')).to_dict())
#       
#        portfolio['Month']=monthly
#        return_monthly=portfolio.groupby('Month').aggregate(lambda x: x.iloc[-1]/x.iloc[0]-1).T
#        average_rank=return_monthly.apply(lambda x: x.rank(ascending=False),axis=0).apply(np.mean,axis=1)
#        return_monthly['Average_rank']=average_rank
#        
#        long_short_0=pd.concat([long_short,monthly],axis=1).rename(columns={0:'Winning_rate',1:'Month'})
#        win_rate_by_month=long_short_0.groupby('Month').aggregate(lambda x: np.mean(x>0)).T           
#
#        high_0=pd.concat([high,monthly],axis=1).rename(columns=lambda x: 'Winning_rate' if x !=0 else 'Month')
#        low_0=pd.concat([low,monthly],axis=1).rename(columns=lambda x: 'Winning_rate' if x !=0 else 'Month')
#        win_rate_daily=(long_short>0).mean()
#        win_rate_monthly=np.mean((high_0.groupby('Month').aggregate(lambda x: np.prod(x+1)-1).values-low_0.groupby('Month').aggregate(lambda x: np.prod(x+1)-1).values)>0)
#        win_rate_by_month['Daily']=win_rate_daily
#        win_rate_by_month['Monthly']=win_rate_monthly   
#        
#        Dict3[factor]=pd.concat([return_monthly,win_rate_by_month],axis=0) 
#
#        port_best=portfolio_info.sort_values(by='annual_return',ascending=False).iloc[0,:]
#        port_best=pd.concat([port_best,long_short_info.rename(lambda x: 'long_short_'+x)]).rename(factor)
#        port_best['long_short_win_ratio_monthly']=win_rate_monthly  
#        port_best['long_short_win_ratio_daily']=win_rate_daily
#        port_best['order']='>'.join(portfolio_info.sort_values('rank').index)
#        port_best['long_short_order']=inx_high+'-'+inx_low
#        port_best['start_time']=datetime.strftime(portfolio.index[0],'%Y%m%d')
#        port_best['end_time']=datetime.strftime(portfolio.index[-1],'%Y%m%d')
#        
#        Table2=Table2.append(port_best)
#    Table2=Table2.drop('rank',axis=1)
#    t1=tm.time()
#    print('\r\tBack Test Summary \t          finished          ')
#    print('total time: %.3f s'%(t1-t0))
#    return Dict1,Table2,Dict3
def bt_figure(Backtest,reference_flag=False,save_path=None,reference_path=None,show_plot=False,**kwarg):
    '''        
    draw figures for backtest result
    '''
    print('\tBack Test Plot \t          start          ')
    warnings.simplefilter(action = "ignore", category = RuntimeWarning)
    reference_flag=(reference_flag if reference_path is not None else False)
    reference_df=pd.DataFrame()
    if reference_flag is True:
        for file_name in glob(reference_path+'\*.csv'):          
            reference_name=file_name.split('\\')[-1].split('.')[0]
            reference=read_file(file_name,header=None)
            reference.iloc[:,0]=reference.iloc[:,0].map(lambda x : datetime.strptime(x,'%Y-%m-%d'))
            reference=reference.set_index(0)[2].rename(reference_name)
            reference_df[reference_name]=reference

    Value_dict={}
    fac_counts=0
    fac_len=len(Backtest)
    for factor in Backtest.keys():           
        if (save_path is not None) and (not os.path.exists(save_path)):
            os.makedirs(save_path)
        fac_counts+=1
        portfolio=deepcopy(Backtest[factor])
        Value=pd.merge(left=portfolio,right=reference_df,left_index=True,right_index=True,how='left')
        Value.loc[Value.index[0],reference_df.columns]=Value.loc[Value.index[0],reference_df.columns].fillna(Value[reference_df.columns].dropna().iloc[0])
        Value=Value/Value.iloc[0]-1

        one_year=250
        high=portfolio.iloc[:,0].pct_change().fillna(0)
        inx_high=portfolio.columns[0] #p0
        low=portfolio.iloc[:,-1].pct_change().fillna(0)
        inx_low=portfolio.columns[-1] #p4
        long_short=high-low #daily return
        long_short_annual_return_tmp=(np.prod(long_short+1)**(one_year/len(long_short))-1 if len(long_short)>0 else np.nan)
        if long_short_annual_return_tmp is not np.nan:
            if long_short_annual_return_tmp<0: 
                long_short*=-1
                high,low=low,high
                inx_high,inx_low=inx_low,inx_high
        Value['long_short (%s - %s)'%(inx_high,inx_low)]=(np.cumprod(1+long_short.values)-1)
        Value_dict[factor]=Value

        sns.set_style("darkgrid")
        sns.set_palette(sns.color_palette("Set2", 15))            
        plt.figure(figsize=(18,10),dpi=100)            
        plt.plot(Value.drop('long_short (%s - %s)'%(inx_high,inx_low),axis=1))   
        plt.fill_between(Value.index,0,Value['long_short (%s - %s)'%(inx_high,inx_low)],color='cornsilk')
        plt.legend(Value,loc='best',fontsize=11)
        plt.gcf().autofmt_xdate()
        plt.title(factor)
        if save_path is not None:
            plt.savefig(save_path+ '\\_'+factor+'.png')
        if show_plot:
            plt.show()
        else:
            plt.close('all')
            print('\r\tBack Test Plot in progress \t step %d/%d  %s'%(fac_counts,fac_len,factor),end='\r')
    print('\r\tBack Test Plot \t          finished          ')
    return Value_dict