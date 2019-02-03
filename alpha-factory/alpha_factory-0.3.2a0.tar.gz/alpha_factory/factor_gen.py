# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 16:32:58 2018

@author: yili.peng
"""

from .cprint import cprint
from .check_mem import clean
from .generator_core import generate_batch 
from .ic_summary import run_all_ic,run_plot_ic,run_ic_summary
from .utilise import find_all_factors,find_factor_name,find_part,align_parms,find_all_parts
from .check_validation import not_na,not_same
from single_factor_model import run_back_test,run_plot,run_plot_turnover,summary,calc_return
from data_box import data_box
from RNWS import read
import os
import numpy as np
import pandas as pd
import time
import warnings
warnings.simplefilter('ignore')

def find_dependency(df):
    return tuple(df.index[df['dependency'].isnull()])

class generator_class:
    def __init__(self,df,factor_path,**parms):
        '''
        df: factor dataframe
        factor_path: root path to store factors
        **parms: all dependency dataframes
        '''
        flag=[i in parms.keys() for i in df.loc[df['dependency'].isnull(),'df_name']]
        if not all(flag):
            print('dependency:',find_dependency(df))
            raise Exception('need all dependencies')
        self.parms=align_parms(parms)
        self.df=df
        self.batch_num=find_part(factor_path)
        self.factor_path=factor_path
        self.d={}
        self.db=None
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):        
        pass
    def reload_factors(self,align=False,store_method='byTime',pre_check=False,**kwargs):
        '''
        align: align factor data
        store_method: 'byTime' or 'byFactor'
        pre_check: filter loaded factors
        '''
        if store_method == 'byTime':        
            factor_list=find_all_factors(self.factor_path)
            if len(factor_list)==0:
                return 
            else:
                for l in factor_list:
                    path=l[0]
                    factors=l[1]
                    cprint('reload: ',path)                    
                    factor_exposures=read.read_df(path=path,file_pattern='factor',header=0,dat_col=factors,**kwargs)
                    for i in range(len(factors)):
                        factor_name=factors[i]
                        factor_value=factor_exposures[i]
                        if pre_check:
                            if not_na(factor_value) and not_same(factor_value):
                                self.parms.update({factor_name: factor_value})
                                self.d.update({factor_name: factor_value})
                            else:
                                self.df.query('df_name!="{}"'.format(factor_name),inplace=True)
                                cprint('{} not valid'.format(factor_name))
                        else:
                            self.parms.update({factor_name: factor_value})
                            self.d.update({factor_name: factor_value})
                    
        elif store_method == 'byFactor':
            parts_list=find_all_parts(self.factor_path)
            if len(parts_list) == 0:
                return            
            for path in parts_list:
                factor_dict=read.read_factors_to_dict(path=path,file_pattern='factor')
                if pre_check:
                    for factor_name,factor_value in factor_dict.items():
                        if not_na(factor_value) and not_same(factor_value):
                            self.parms.update({factor_name: factor_value})
                            self.d.update({factor_name: factor_value})
                        else:
                            self.df.query('df_name!="{}"'.format(factor_name),inplace=True)
                            cprint('{} not valid'.format(factor_name))
                else:
                    self.parms.update(factor_dict)
                    self.d.update(factor_dict)
        else:
            raise Exception('wrong value of store_method')
            
        if align:
            self.parms=align_parms(self.parms)

    def reload_factors_part(self,specific_path,pre_check=False,store_method='byTime',**kwargs):
        '''
        This is for running back test purpose only
        '''
        self.d={}
        if store_method == 'byTime':
            factors=find_factor_name(specific_path)
            cprint('reload: ',specific_path)
            factor_exposures = read.read_df(path=specific_path,file_pattern='factor',header=0,dat_col=factors,**kwargs)
            
            for i in range(len(factors)):
                factor_name=factors[i]
                factor_value=factor_exposures[i]
                if pre_check:
                    if not_na(factor_value) and not_same(factor_value):
                        self.d.update({factor_name: factor_value})
                    else:
                        self.df.query('df_name!="{}"'.format(factor_name),inplace=True)
                        cprint('{} not valid'.format(factor_name))
                else:
                    self.d.update({factor_name: factor_value})
        elif store_method == 'byFactor':
            factor_dict=read.read_factors_to_dict(path=specific_path,file_pattern='factor')
            if pre_check:
                for factor_name,factor_value in factor_dict.items():
                    if not_na(factor_value) and not_same(factor_value):
                        self.d.update({factor_name: factor_value})
                    else:
                        self.df.query('df_name!="{}"'.format(factor_name),inplace=True)
                        cprint('{} not valid'.format(factor_name))
            else:
                self.d.update(factor_dict)
        else:
            raise Exception('wrong value of store_method')

    def reload_df(self,path,**kwargs):
        self.df=pd.read_csv(filepath_or_buffer=path,**kwargs)
    def output_df(self,path,**kwargs):
        self.df.to_csv(path_or_buf=path,index=False,**kwargs)
    def generator(self,name_start='a',store_method='byTime',batch_size=50,debug_mode=False):
        '''
        multiprocessing is deprecated due to vast memory sharing problem
        '''
        cprint('\nGenerating one batch start',c='',f='l')
        t0=time.time()
        new_df,new_parms,d=generate_batch(self.df,batch_size=batch_size,out_file_path=self.factor_path+'/factor_part'+str(self.batch_num).zfill(3),name_start=name_start,store_method=store_method,debug_mode=debug_mode,**self.parms)
        self.parms.update(new_parms)
        self.df=new_df
        self.batch_num+=1
        t1=time.time()
        cprint('Generating one batch finished --- time %.3f s\n'%(t1-t0),c='',f='l')
        self.d=d
        new_df=new_parms=t0=t1=None
        clean()
    def getOrCreate_databox(self,price=None,ind=None,ind_weight=None,sus=None,path=None):
        '''
        path: None(default) or the path to save databox (and reload next time when this function is called).
        '''
        if path is None:
            cprint('\nCreating data box',c='',f='l')
            assert isinstance(price,pd.DataFrame) and isinstance(ind,pd.DataFrame) and isinstance(ind_weight,pd.DataFrame) and isinstance(sus,pd.DataFrame),'please input dataframe'
            self.db=data_box()\
                .load_adjPrice(price)\
                .load_indestry(ind)\
                .load_indexWeight(ind_weight)\
                .load_suspend(sus)\
                .calc_indweight()\
                .set_lag(freq='d',day_lag=0)
        elif os.path.exists(path):
            cprint('\nLoading data box',c='',f='l')
            self.db=data_box()\
                    .load(path)        
        else:
            cprint('\nCreating data box',c='',f='l')
            assert isinstance(price,pd.DataFrame) and isinstance(ind,pd.DataFrame) and isinstance(ind_weight,pd.DataFrame) and isinstance(sus,pd.DataFrame),'please input dataframe'
            self.db=data_box()\
                    .load_adjPrice(price)\
                    .load_indestry(ind)\
                    .load_indexWeight(ind_weight)\
                    .load_suspend(sus)\
                    .calc_indweight()\
                    .set_lag(freq='d',day_lag=0)\
                    .save(path)                
        for f,df in self.d.items():
            self.db.add_factor(f,df)
        cprint('\nAligning data',c='',f='l')
        self.db.align_data()
        
    def back_test(self,sharpe_ratio_thresh=3,n=5,out_path=None,back_end='loky',n_jobs=-1,detail_root_path=None,double_side_cost=0.003,rf=0.03,**kwargs):
        '''
        Before back_test, data_box must be created by function create_data_box and aligned
        '''
        out_path= os.path.join(self.factor_path,'..') if out_path is None else out_path        
        
        cprint('\nRun backtesting start',c='',f='l')
        
        Value,Turnover=run_back_test(self.db,n=n,back_end=back_end,n_jobs=n_jobs,out_path=detail_root_path,double_side_cost=double_side_cost,**kwargs)
        
        Re=calc_return(Value,Turnover,long_short=True,double_side_cost=double_side_cost)
        
        S=summary(Re,annual_risk_free=rf,only_total=True)
        
        SS_pos=S.query('(stats=="Sharpe_Ratio")&(portfolio=="long_short_positive")')[['factor','value']]
        SS_neg=S.query('(stats=="Sharpe_Ratio")&(portfolio=="long_short_negative")')[['factor','value']]        
        SS_pos2=pd.Series(SS_pos.value.values,index=SS_pos.factor.values)
        SS_neg2=pd.Series(SS_neg.value.values,index=SS_neg.factor.values)
        SS=np.maximum(SS_neg2,SS_pos2)
        
        chosen_factors=SS.loc[SS.gt(sharpe_ratio_thresh)].index.tolist()
        
        cprint('\nRun backtesting end, output figures',c='',f='l')
        
        run_plot(Re[chosen_factors],save_path=out_path+'/figure')
        run_plot_turnover(Turnover[chosen_factors],save_path=out_path+'/figure')
        
        output_s=os.path.join(out_path,'SS')
        if not os.path.exists(output_s):
            os.makedirs(output_s)      
        SS.to_csv(output_s+'/SS.csv',header=False,mode='a')
        
    def icir(self,ir_thresh=1,out_path=None,back_end='loky',n_jobs=-1,periods=1,**kwargs):
        out_path = os.path.join(self.factor_path,'..') if out_path is None else out_path
        cprint('\nRun ic-ir start',c='',f='l')
        
        IC=run_all_ic(self.db,periods=[periods],n_jobs=n_jobs,back_end=back_end,**kwargs)
        S=run_ic_summary(IC)
        SS=S.xs('{}D'.format(periods),level=1,axis=1).iloc[2]
        chosen_factors=SS.loc[SS.abs().gt(ir_thresh)].index.tolist()
        
        cprint('\nRun ic-ir end, output figures',c='',f='l')
        run_plot_ic(IC[chosen_factors],save_path=out_path+'/figure')
        
        output_s=os.path.join(out_path,'SS')
        if not os.path.exists(output_s):
            os.makedirs(output_s)
        SS.to_csv(output_s+'/SS_icir.csv',header=False,mode='a')