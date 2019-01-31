# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 15:43:12 2019

@author: yili.peng
"""

import empyrical as em
import pandas as pd
from joblib import Parallel,delayed
from multiprocessing import Pool
import matplotlib.pyplot as plt
import os

def win_rate(Return):
    return Return.apply(lambda x: x.loc[(x!=0)&(~x.isna())].ge(0).mean())

def plr(Return):
    return Return.apply(lambda x:x.loc[x>0].mean()/x.loc[x<0].mul(-1).mean())

def calc_basics(Return,name,annual_risk_free=0.03):
    risk_free=annual_risk_free/252
    return pd.DataFrame([em.annual_return(Return).values,
                         em.max_drawdown(Return).values,
                         em.sharpe_ratio(Return,risk_free=risk_free),
                         em.sortino_ratio(Return,required_return=risk_free).values,
                         win_rate(Return).values,
                         plr(Return).values
                         ]
                        ,columns=Return.columns
                        ,index=pd.Index(['Annual_Return','Max_Drawndown','Sharpe_Ratio','Sortino_Ratio','Win_Rate','PnL_ratio'],name='stats')
                        ).unstack().rename(name)

def calc_return(Value,Turnover=None,long_short=False,double_side_cost=0):
    '''
    If long_short is True, Turnover must be assigned.    
    
    How to calculate long short return:
        
    for original portfolio
    V_2^p0 = V_1^p0 * (1 + R^p0) * (1 - T^p0 * r) # V: Value, R: stock return, T: turnover, r: double side cost, p0: portfolio 0
    V_2^p4 = V_1^p4 * (1 + R^p4) * (1 - T^p4 * r) # V: Value, T: stock return, T: turnover, r: double side cost, p4: portfolio 4
    
    if no double_side_cost, portfolio return defined as 
    tild(R_2^p0) := V_2^p0 / V_1^p0 -1 
                  = R_2^p0 
    
    if has double_side_cost 
    tild(R_2^p0) := V_2^p0 / V_1^p0 -1 
                  = (1 + R^p0) * (1 - T^p0 * r) - 1
    thus 
    R^p0 = V_2^p0 / V_1^p0 / (1 - T^p0 * r) - 1
    
    long_short return for stock
    R^delta = R^p0 - R^p4
    
    value for long_short portfolio
    V_2^delta = V_1^delta * (1 + R^delta ) * (1 - (T^p0 + T^p4)/2 * r)
    
    return for long_short portfolio
    tild(R^delta) := V_2^delta / V_1^delta - 1 
                   = (1 + R^delta ) * (1 - (T^p0 + T^p4)/2 * r) - 1
    '''
    Return=Value.unstack(0).pct_change().fillna(0)
    if not long_short:
        return Return.stack(dropna=False).swaplevel().sort_index()
    else:
        assert isinstance(Turnover,pd.DataFrame), 'Turnover should be pandas dataframe'
        
        stacked_Return=Return.stack(0,dropna=False)
        stacked_Trunover=Turnover.unstack(0).stack(0,dropna=True)
        assert stacked_Trunover.shape[1] > 1, 'long short requires at least 2 portfolio'
        
        Return_delta = (1 + stacked_Return.iloc[:,0] ) / (1 - stacked_Trunover.iloc[:,0]*double_side_cost) - (1 + stacked_Return.iloc[:,-1] ) / (1 - stacked_Trunover.iloc[:,-1]*double_side_cost) 
        stacked_Return['long_short_positive'] = (1 + Return_delta) * ( 1 - (stacked_Trunover.iloc[:,0] + stacked_Trunover.iloc[:,-1])/2 * double_side_cost ) - 1
        stacked_Return['long_short_negative'] = (1 - Return_delta) * ( 1 - (stacked_Trunover.iloc[:,0] + stacked_Trunover.iloc[:,-1])/2 * double_side_cost ) - 1
        
        return stacked_Return.unstack().stack(0,dropna=False).swaplevel().sort_index()

def summary_core(X):
    Return,factor_name,annual_risk_free=X
    result=[calc_basics(Return,'total',annual_risk_free)]
    for key,group in Return.groupby(by=[Return.index.year,Return.index.month]):
        name=str(key[0]*100+key[1])
        result.append(calc_basics(group,name,annual_risk_free))
    return pd.concat(result,axis=1).rename_axis('period',axis=1).stack().rename(factor_name)

def summary_core_total(X):
    Return,factor_name,annual_risk_free=X
    return calc_basics(Return,factor_name,annual_risk_free)

def summary(Return,annual_risk_free=0.03,back_end=None,n_jobs=-1,only_total=False,**kwargs):
    assert back_end in (None,'loky','multiprocessing'),'wrong backend type'    
    core = summary_core_total if only_total else summary_core
    header=['factor','stats','portfolio'] if only_total else ['factor','period','stats','portfolio']    
    if back_end is None:
        lst=[]
        for f in Return.columns:
            Return_sub=Return[f].unstack(level=0)
            lst.append(core((Return_sub,f,annual_risk_free)))
    
    elif back_end is 'loky':
        lst=Parallel(n_jobs=n_jobs,**kwargs)(
                delayed(core)( (Return[f].unstack(level=0),f,annual_risk_free) 
                                    ) for f in Return.columns)
    else:
        X=[(Return[f].unstack(level=0),f,annual_risk_free) for f in Return.columns]
        pool=Pool(processes=n_jobs,**kwargs)            
        lst=pool.map(core,X)
        pool.close()
        pool.join()
    summarized=pd.concat(lst,axis=1).rename_axis('factor',axis=1).stack().rename('value').reset_index().sort_values(header).reindex(header+['value'],axis=1)
    return summarized

def run_plot(Return,reference_value=None,save_path=None,show=False):
    '''
    reference_value: pd.Series with index as dt
    '''
    assert (reference_value is None) or (type(reference_value) is pd.Series), 'Wrong type of reference value'     
    for f in Return.columns:
        Return_sub=Return[f].unstack(level=0)
#        long_short=(Return.iloc[:,0]-Return.iloc[:,-1]).div(2).add(1).cumprod()
        V=Return_sub.add(1).cumprod()        
        if ('long_short_negative' in V.columns) and ('long_short_positive' in V.columns):
            lsn=V['long_short_negative']
            lsp=V['long_short_positive']
            V=V.drop(['long_short_negative','long_short_positive'],axis=1)
            long_short = lsn if lsn.iloc[-1] > lsp.iloc[-1] else lsp
        else:
            long_short = None
        plt.style.use('ggplot')
        plt.figure(figsize=(18,10),dpi=100)
        plt.plot(V)
        if long_short is not None:
            plt.fill_between(long_short.index,1,long_short,color='cornsilk',label=long_short.name)
            if reference_value is None:
                ll=list(V.columns)+[long_short.name]                
            else:
                plt.plot(reference_value.reindex(V.index).pct_change().add(1).cumprod(),label='Index')                
                ll=list(V.columns)+[long_short.name,'Index']
        else:
            if reference_value is None:
                ll=list(V.columns)
            else:
                plt.plot(reference_value.reindex(V.index).pct_change().add(1).cumprod(),label='Index')                
                ll=list(V.columns)+['Index']                
        plt.legend(ll,loc=2,fontsize=11)        
        plt.title(f)
        plt.gcf().autofmt_xdate()
        if save_path is not None:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            plt.savefig(os.path.join(save_path,'Value_{}.png'.format(f)))
        if show:
            plt.show()
        else: 
            plt.close('all')

def run_plot_turnover(Turnover,save_path=None,show=False):
    for f in Turnover.columns:
        V=Turnover[f].unstack(level=0)
        plt.style.use('ggplot')
        plt.figure(figsize=(18,10),dpi=100)   
        plt.plot(V)
        plt.title(f)
        plt.legend(V,loc='best',fontsize=11)
        plt.gcf().autofmt_xdate()        
        if save_path is not None:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            plt.savefig(os.path.join(save_path,'Turnover_{}.png'.format(f)))
        if show:
            plt.show()
        else: 
            plt.close('all')