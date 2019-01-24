# -*- coding: utf-8 -*-
"""
Created on Fri Jun  8 16:32:58 2018

@author: yili.peng
"""

from .cprint import cprint
from .check_mem import clean
from .generator_core import generate_batch 
from .ic_summary import run_all_ic,run_plot_ic,run_ic_summary
from single_factor_model import run_back_test,run_plot,run_plot_turnover,summary,calc_return
from data_box import data_box
from RNWS import read_df
import os
import numpy as np
from glob import glob
import pandas as pd
import time
import warnings
warnings.simplefilter('ignore')

def find_dependency(df):
    return tuple(df.index[df['dependency'].isnull()])

def find_all_factors(path):
    pathlist=[[i,glob(i+'/factor_[0-9]*.csv')[1]] for i in glob(path+'/factor_part[0-9]*')]
    factor_list=[]
    for p in pathlist:
        line=open(p[1],'r').readline()
        factor_list.append([p[0],line.strip('\n').split(',')[1:]])
    return factor_list

def find_factor_name(specific_path):
    p=glob(specific_path + '/factor_[0-9]*.csv')[0]
    line=open(p,'r').readline()
    factor_names=line.strip('\n').split(',')[1:]
    return factor_names
    
def find_part(path):
    try:
        a=max([int(i[-3:]) for i in glob(path+'/*')])+1
    except:
        a=0
    return a

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
        self.parms=parms
        self.df=df
        self.batch_num=find_part(factor_path)
        self.factor_path=factor_path
        self.d={}
        self.db=None
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    def reload_factors(self,**kwargs):
        factor_list=find_all_factors(self.factor_path)
        if len(factor_list)==0:
            pass
        else:
            for l in factor_list:
                path=l[0]
                factors=l[1]
                print('reload: ',path)
                factor_exposures=read_df(path=path,file_pattern='factor',header=0,dat_col=factors,**kwargs)
                self.parms.update({factors[i]:factor_exposures[i] for i in range(len(factors))})
                self.d.update({factors[i]:factor_exposures[i] for i in range(len(factors))})
    def reload_factors_part(self,specific_path,**kwargs):
        '''
        This is for load one part and run back test only
        '''
        self.d={}        
        factors=find_factor_name(specific_path)
        factor_exposures = read_df(path=specific_path,file_pattern='factor',header=0,dat_col=factors,**kwargs)        
        self.d.update({factors[i]:factor_exposures[i] for i in range(len(factors))})
        
    def reload_df(self,path,**kwargs):
        self.df=pd.read_csv(filepath_or_buffer=path,**kwargs)
    def output_df(self,path,**kwargs):
        self.df.to_csv(path_or_buf=path,index=False,**kwargs)
    def generator(self,name_start='a',batch_size=50):
        '''
        multiprocessing is deprecated due to vast memory sharing problem
        '''
        cprint('\nGenerating one batch start',c='',f='l')
        t0=time.time()
        new_df,new_parms,d=generate_batch(self.df,batch_size=batch_size,out_file_path=self.factor_path+'/factor_part'+str(self.batch_num).zfill(3),name_start=name_start,**self.parms)
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
            cprint('\nCreating data box')
            assert isinstance(price,pd.DataFrame) and isinstance(ind,pd.DataFrame) and isinstance(ind_weight,pd.DataFrame) and isinstance(sus,pd.DataFrame),'please input dataframe'
            self.db=data_box()\
                .load_adjPrice(price)\
                .load_indestry(ind)\
                .load_indexWeight(ind_weight)\
                .load_suspend(sus)\
                .calc_indweight()\
                .set_lag(freq='d',day_lag=0)
        elif os.path.exists(path):
            cprint('\nLoading data box')
            self.db=data_box()\
                    .load(path)        
        else:
            cprint('\nCreating data box')
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
        cprint('\nAligning data')
        self.db.align_data()
        
    def back_test(self,sharpe_ratio_thresh=3,n=5,out_path=None,back_end='loky',n_jobs=-1,detail_root_path=None,double_side_cost=0.003,rf=0.03,**kwargs):
        '''
        Before back_test, data_box must be created by function create_data_box and aligned
        '''
        out_path= os.path.join(self.factor_path,'..') if out_path is None else out_path        
        
        cprint('\nRun backtesting start')
        
        Value,Turnover=run_back_test(self.db,n=n,back_end=back_end,n_jobs=n_jobs,weight_path=detail_root_path,double_side_cost=double_side_cost,**kwargs)
        
        Re=calc_return(Value,Turnover,long_short=True,double_side_cost=double_side_cost)
        
        S=summary(Re,annual_risk_free=rf,only_total=True)
        
        SS_pos=S.query('(stats=="Sharpe_Ratio")&(portfolio=="long_short_positive")')[['factor','value']]
        SS_neg=S.query('(stats=="Sharpe_Ratio")&(portfolio=="long_short_negative")')[['factor','value']]        
        SS_pos2=pd.Series(SS_pos.value.values,index=SS_pos.factor.values)
        SS_neg2=pd.Series(SS_neg.value.values,index=SS_neg.factor.values)
        SS=np.maximum(SS_neg2,SS_pos2)
        
        chosen_factors=SS.loc[SS.gt(sharpe_ratio_thresh)].index.tolist()
        
        cprint('\nRun backtesting end, output figures')
        
        run_plot(Re[chosen_factors],save_path=out_path+'/figure')
        run_plot_turnover(Turnover[chosen_factors],save_path=out_path+'/figure')
        
        output_s=os.path.join(out_path,'SS')
        if not os.path.exists(output_s):
            os.makedirs(output_s)      
        SS.to_csv(output_s+'/SS.csv',header=False,mode='a')
        
    def icir(self,ir_thresh=1,out_path=None,back_end='loky',n_jobs=-1,**kwargs):
        out_path = os.path.join(self.factor_path,'..') if out_path is None else out_path
        cprint('\nRun ic-ir start')
        
        IC=run_all_ic(self.db,periods=[1],n_jobs=n_jobs,back_end=back_end,**kwargs)
        S=run_ic_summary(IC)
        SS=S.xs('1D',level=1,axis=1).iloc[2]
        chosen_factors=SS.loc[SS.abs().gt(ir_thresh)].index.tolist()
        
        cprint('\nRun ic-ir end, output figures')
        run_plot_ic(IC[chosen_factors],save_path=out_path+'/figure')
        
        output_s=os.path.join(out_path,'SS')
        if not os.path.exists(output_s):
            os.makedirs(output_s)      
        SS.to_csv(output_s+'/SS_icir.csv',header=False,mode='a')