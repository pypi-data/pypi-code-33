# -*- coding: utf-8 -*-
"""
Created on Wed May  9 16:42:41 2018

@author: yili.peng
"""

import warnings
import pandas as pd
from multiprocessing import Pool
from joblib import Parallel,delayed
import time as tm
#from .global_func import seperate
from .global_func import seperate_new,portfolio_pct_change

#
#def back_test_new_core(X):
#    '''
#    one_time trading is a three day process
#    day one: calculate factor (check suspend, whether specific tickers can be traded)
#    day two: open position (check suspend, whether specific tickers can be traded)
#    day three: close position (check suspend, whether specific tickers can be traded)
#    '''
#    n,Dict=X
#    df_pri=Dict['Price']
#    df_ret=df_pri.pct_change()
#    df_fac=Dict['Factor']
#    df_ind=Dict['Industry']
#    df_sus=Dict['Suspend']
#    df_ind_weight=Dict['Industry_Weight']       
#    ports=['p%d'%i for i in range(n)]
#    times=df_fac.index
#    tickers=df_fac.columns
#    m=len(times)
#    # check availability
#    if len(times)==0 or len(tickers)==0:
#        raise Exception('wrong shape of input')        
#    # initialize
#    portfolio_weight=pd.DataFrame(0,index=tickers,columns=ports)
#    portfolio_vacant=pd.Series(1000,index=ports)
#    portfolio_value=portfolio_vacant.rename(times[0]).to_frame().T
#    if m==1:
#        return portfolio_value
#
#    for i in range(1,m):
#        
#        t_1=times[i-1]
#        t=times[i]
#
#        # freeze (t)
#        # cannot close position
#        port_sus=pd.DataFrame([df_sus.loc[t].eq(1)]*n,index=ports).T
#        portfolio_freezer=portfolio_weight.where(port_sus).fillna(0)
#        
#        # change position (t)
#        ## new weight
#        ava_sample=pd.concat([df_fac.loc[t_1].rename('Factor')
#                        ,df_ind.loc[t_1].rename('Industry')
#                        ,df_sus.loc[t].rename('Suspend')]
#                        ,axis=1).dropna(axis=0).query('Suspend==0')
#        ava_ind=df_ind_weight.loc[t_1]\
#                            .loc[ava_sample['Industry'].unique()]
#        if ava_ind.sum()>0:
#            ava_ind_weight=ava_ind/ava_ind.sum()
#        elif ava_ind.shape[0]>0:
#            ava_ind_weight=pd.Series(1/ava_ind.shape[0],index=ava_ind.index)
#        else:
#            # no available factor at all
#            # do not change position
#            continue
#        ## new position
#        ava_weights=[]
#        for ind,weight_of_ind in ava_ind_weight.items():
#            tickers_of_ind=ava_sample.query('Industry==%s'%str(ind)).sort_values(by='Factor',ascending=False).index.tolist()
#        #    port_weights_of_ind=seperate(tickers_of_ind,n).rename(index={i:'p'+str(i) for i in range(n)})*weight_of_ind
#            port_weights_of_ind=seperate_new(tickers_of_ind,n).rename(index={i:'p'+str(i) for i in range(n)})*weight_of_ind
#            ava_weights.append(port_weights_of_ind)
#        new_portfolio_weight=pd.concat(ava_weights,axis=1).T
#        # redistribute weight
#        unfrozen_weight=new_portfolio_weight.sum()-portfolio_freezer.sum()            
#        portfolio_weight2=new_portfolio_weight.mul(unfrozen_weight).add(portfolio_freezer,fill_value=0)
#        
#        # valuate (t)
#        # portfolio_weight before changing position 
#        ret=df_ret.loc[t].fillna(0)
#        new_value=portfolio_value.loc[t_1]\
#                            .mul(
#                                portfolio_weight.mul(ret.add(1),axis=0).sum()
#                                )\
#                            .rename(t)
#        
#        if portfolio_weight.sum().sum()==0:
#            # hold no position
#            new_value+=portfolio_vacant
#        weight_diff=portfolio_pct_change(portfolio_weight,portfolio_weight2)
#        portfolio_value=portfolio_value.append(new_value*(1-weight_diff))
#        
#        #update portfolio weight
#        portfolio_weight=portfolio_weight2
#
#    return portfolio_value

def back_test_new_core(X):
    '''
    one_time trading is a three day process
    day one: calculate factor (check suspend, whether specific tickers can be traded)
    day two: open position (check suspend, whether specific tickers can be traded)
    day three: close position (check suspend, whether specific tickers can be traded)
    '''
    n,Dict=X
    df_pri=Dict['Price']
    df_ret=df_pri.pct_change()
    df_fac=Dict['Factor']
    df_ind=Dict['Industry']
    df_sus=Dict['Suspend']
    df_ind_weight=Dict['Industry_Weight']       
    ports=['p%d'%i for i in range(n)]
    times=df_fac.index
    tickers=df_fac.columns
    m=len(times)
    # check availability
    if len(times)==0 or len(tickers)==0:
        raise Exception('wrong shape of input')        
    # initialize
    portfolio_weight=pd.DataFrame(0,index=tickers,columns=ports)
    portfolio_vacant=pd.Series(1000,index=ports)
    portfolio_value=portfolio_vacant.rename(times[0]).to_frame().T
    if m==1:
        return portfolio_value

    for i in range(1,m):
        print(i)
        t_1=times[i-1]
        t=times[i]

        # freeze (t)
        # cannot close position
        port_sus=pd.DataFrame([df_sus.loc[t].eq(1)]*n,index=ports).T
        portfolio_freezer=portfolio_weight.where(port_sus).fillna(0)
        
        # change position (t)
        ## new weight
        ava_sample=pd.concat([df_fac.loc[t_1].rename('Factor')
                        ,df_ind.loc[t_1].rename('Industry')
                        ,df_sus.loc[t].rename('Suspend')]
                        ,axis=1).dropna(axis=0).query('Suspend==0')
        ava_ind=df_ind_weight.loc[t_1]\
                            .loc[ava_sample['Industry'].unique()]
        
        if ava_ind.shape[0]>0:
            # exists valid tickers and factor values
            if ava_ind.sum()>0:
                # valid industries are in index
                ava_ind_weight=ava_ind/ava_ind.sum()
            else:
                # valid industries aren't in index
                ava_ind_weight=pd.Series(1/ava_ind.shape[0],index=ava_ind.index)
            ava_weights=[]
            for ind,weight_of_ind in ava_ind_weight.items():
                tickers_of_ind=ava_sample.query('Industry==%s'%str(ind)).sort_values(by='Factor',ascending=False).index.tolist()
            #    port_weights_of_ind=seperate(tickers_of_ind,n).rename(index={i:'p'+str(i) for i in range(n)})*weight_of_ind
                port_weights_of_ind=seperate_new(tickers_of_ind,n).rename(index={i:'p'+str(i) for i in range(n)})*weight_of_ind
                ava_weights.append(port_weights_of_ind)
            new_portfolio_weight=pd.concat(ava_weights,axis=1).T
        else:
            new_portfolio_weight=portfolio_weight
            
        # redistribute weight
        unfrozen_weight=new_portfolio_weight.sum()-portfolio_freezer.sum()
        portfolio_weight2=new_portfolio_weight.mul(unfrozen_weight).add(portfolio_freezer,fill_value=0)
        
        # valuate (t)
        # portfolio_weight before changing position 
        ret=df_ret.loc[t].fillna(0)
        new_value=portfolio_value.loc[t_1]\
                            .mul(
                                portfolio_weight.mul(ret.add(1),axis=0).sum()
                                )\
                            .rename(t)
        
        if portfolio_weight.sum().sum()==0:
            # hold no position
            new_value+=portfolio_vacant
        weight_diff=portfolio_pct_change(portfolio_weight,portfolio_weight2).rename(t)
        portfolio_value=portfolio_value.append(new_value*(1-weight_diff))
        
        #update portfolio weight
        portfolio_weight=portfolio_weight2

    return portfolio_value

class back_testing:
    def __init__(self,factor_dict={}):
        '''
        initialization
        
        factor_dict: the dictionary returned from preprocessing
        '''
        self.factor_dict=factor_dict
        warnings.simplefilter(action = "ignore", category = RuntimeWarning)
    def __call__(self,**kwarg):
        '''
        run back testing
        '''
        t0=tm.time()
        print('\n--------------------[ Back Testing Start ]--------------------')
        self.update(**kwarg)
        B=self.back_test(**kwarg)
        t1=tm.time()
        print('total time: %.3f s'%(t1-t0))
        print('--------------------[ Back Testing End ]--------------------\n')
        return B
    def update(self,new_dict={},**kwarg):
        '''    
        update factor_dict
        
        new_dict={'Factor_name1':Factor1_info,'Factor_name2':Factor2_info,...}
        Factor_info={'Return':Return_df,'Industry':Industry_df,'Factor':Factor_df,'Stock_Weight':Stock_Weight_df,'Industry_Weight':Industry_Weight_df,'Time':Time_list,'Multiple':Multiple_df}
        '''
        self.factor_dict.update(new_dict)

    def back_test(self,n=5,sub_factor=None,processors=None,test_mode=False,back_end='loky',**kwarg):
        '''
        back test w/ multiprocessing
        
        n: portfolio numbers, default=5
        sub_factor: list/tuple or None(all)
        processors: number of processors
        back_end: 'loky' (default) or 'multiprocess'
        '''
        if sub_factor is None:
            factor_list=list(self.factor_dict.keys())
        else:
            factor_list=list(set(sub_factor) & set(self.factor_dict.keys()))
        if len(factor_list)==0:
            raise Exception('No effcient factor')
        if not test_mode:
            if back_end=='loky':
                multi_res=Parallel(n_jobs=processors,verbose=40)(delayed(back_test_new_core)((n,self.factor_dict[factor])) for factor in factor_list)
            elif back_end=='multiprocess':
                pool=Pool(processes=processors)
                X=[((n,self.factor_dict[factor])) for factor in factor_list]
                multi_res=pool.map(back_test_new_core,X)
                pool.close()
                pool.join()
            else:
                raise Exception('Back_end not support. Use loky or multiprocess')
        else:
            multi_res=[]
            for factor in factor_list:
                print(factor)
                multi_res.append(back_test_new_core((n,self.factor_dict[factor])))
        Backtest={fac:res for fac,res in zip(factor_list,multi_res)}
        return Backtest