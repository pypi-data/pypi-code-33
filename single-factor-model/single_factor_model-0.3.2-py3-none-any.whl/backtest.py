# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 13:52:38 2019

@author: yili.peng
"""

import pandas as pd
import os
from joblib import Parallel,delayed
from multiprocessing import Pool
from .utilise import seperate
import itertools

def _calc_s_f(s2,r):
    return s2.mul(r.add(1,fill_value=0),axis=0)
def _calc_ss(s_f,sus,n):
    n=s_f.shape[1]
    port_sus=pd.DataFrame([sus.eq(1)]*n,index=s_f.columns).T
    return s_f.where(port_sus).fillna(0)
def _calc_sv_f(s_f,ss):
    return s_f.sub(ss,fill_value=0)
def _calc_cost_f(sv_f,c2,cost_rate=0.0015):
    return (2*sv_f.sum()+c2)*cost_rate
def _calc_weight(factor_value2,ind,sus,ind_weight2,n):
    ava_sample=pd.concat([factor_value2.rename('Factor')
                        ,ind.rename('Industry')
                        ,sus.rename('Suspend')],axis=1)\
                .dropna(axis=0).query('Suspend==0')
    if ava_sample.shape[0]>0:
        # exists valid tickers and factor values and industries        
        ava_ind=ind_weight2.loc[ava_sample['Industry'].unique()]        
        if ava_ind.sum()>0:
            # valid industries are in index
            ava_ind_weight=ava_ind/ava_ind.sum()
        else:
            # valid industries aren't in index
            ava_ind_weight=pd.Series(1/ava_ind.shape[0],index=ava_ind.index)
        ava_weights=[]
        for industry,weight_of_ind in ava_ind_weight.items():
            tickers_of_ind=ava_sample.query('Industry=={}'.format(industry)).sort_values(by='Factor',ascending=False).index.tolist()
            port_weights_of_ind=seperate(tickers_of_ind,n).rename(index={i:'p'+str(i) for i in range(n)})*weight_of_ind
            ava_weights.append(port_weights_of_ind)
        weight_distribute=pd.concat(ava_weights,axis=1).T
    else:
        weight_distribute=pd.DataFrame(columns=['p'+str(i) for i in range(n)]) # no weight assigned
    return weight_distribute
def _calc_sv(weight,cost_f,c2,sv_f):
    ava_v=c2+sv_f.sum()-cost_f
    return weight.mul(ava_v)
def _calc_s(ss,sv):
    return ss.add(sv,fill_value=0)
def _calc_cost(sv,sv_f,cost_rate=0.0015):
    return sv.sub(sv_f,fill_value=0).abs().sum()*cost_rate
def _calc_c(c2,sv_f,sv,cost):
    return c2+sv_f.sum()-sv.sum()-cost
def _calc_v(c,s):
    return s.sum()+c

def _calc_turnover(s_f,c2,s):
    v_f=s_f.sum() + c2
    turn = s_f.sub(s,fill_value=0).abs().sum().div(v_f)/2
    return turn
def _calc_s_w(v,s):
    return s.div(v)

def _init_portfolio(n,tickers,start_time,start_amount=1000):
    ports=['p'+str(i) for i in range(n)]
    Total_Value=pd.DataFrame(start_amount,columns=ports,index=[start_time]).rename_axis('dt').rename_axis('portfolio',axis=1)
    Stock_Value_tmp=pd.DataFrame(0,columns=ports,index=tickers).rename_axis('tickers').rename_axis('portfolio',axis=1)
    Cash=pd.Series(start_amount,index=ports).rename(start_time).to_frame().T.rename_axis('dt').rename_axis('portfolio',axis=1)
    Turnover=pd.Series(0,index=ports).rename(start_time).to_frame().T.rename_axis('dt').rename_axis('portfolio',axis=1)
    Weight_List=[pd.DataFrame(0,columns=ports,index=tickers).rename_axis('ticker').rename_axis('portfolio',axis=1).unstack().rename(start_time)]
    return Total_Value,Stock_Value_tmp,Cash,Turnover,Weight_List

def back_test_core(X):

    n,Price,Sus,Ind,Ind_Weight,Factor,factor_name,double_side_cost = X
    Re = Price.pct_change()
    times=Factor.index
    tickers=Factor.columns
    m=len(times)
    if len(times)==0 or len(tickers)==0:
        raise Exception('wrong shape of input') 
    Total_Value,Stock_Value_tmp,Cash,Turnover,Weight_List = _init_portfolio(n,tickers,start_time=times[0])
    if m==1:
        return Total_Value,Turnover,pd.concat(Weight_List ,axis=1).rename_axis('dt',axis=1).stack().rename(factor_name) 
    else:        
        s2=Stock_Value_tmp
        for i in range(1,m):
            t_1=times[i-1]
            t=times[i] 
            
            factor_value2=Factor.loc[t_1]
            ind_weight2=Ind_Weight.loc[t_1]
            c2=Cash.loc[t_1]
            ind=Ind.loc[t]
            sus=Sus.loc[t]
            r=Re.loc[t]
            
            s_f=_calc_s_f(s2,r)
            ss=_calc_ss(s_f,sus,n)
            sv_f=_calc_sv_f(s_f,ss)
            cost_f=_calc_cost_f(sv_f,c2,cost_rate=double_side_cost/2)
            weight=_calc_weight(factor_value2,ind,sus,ind_weight2,n)
            sv=_calc_sv(weight,cost_f,c2,sv_f)
            s=_calc_s(ss,sv)
            cost=_calc_cost(sv,sv_f,cost_rate=double_side_cost/2)
            c=_calc_c(c2,sv_f,sv,cost)            
            v=_calc_v(c,s)
            
            # record
            turn=_calc_turnover(s_f,c2,s)
            s_w=_calc_s_w(v,s)            
            Total_Value=Total_Value.append(v.rename(t))
            Turnover=Turnover.append(turn.rename(t))
            Weight_List.append(s_w.unstack().rename(t))
            Cash=Cash.append(c.rename(t))
            # update
            s2=s
        return Total_Value.unstack().rename(factor_name),Turnover.unstack().rename(factor_name),pd.concat(Weight_List,axis=1).rename_axis('dt',axis=1).stack().rename(factor_name),Cash.unstack().rename(factor_name)

def output_weight(Weight,weight_path,ind,ind_weight,sus,fac,ind_spc=None):    
    if weight_path is None:
        return
    if not os.path.exists(weight_path):
        os.makedirs(weight_path)
    for f in Weight.columns:        
        weight_df=Weight[f].unstack(level=0).swaplevel(axis=0).sort_index(axis=0).mul(100)        
        Sus=sus.stack().rename('sus').reindex(weight_df.index)        
        ind_df=ind.stack().rename('ind').reset_index()
        ind_weight_df=ind_weight.stack().rename('ind_weight').reset_index()
        Industry=pd.merge(ind_df,ind_weight_df,on=['dt','ind'],how='outer').set_index(['dt','ticker']).reindex(weight_df.index)        
        Fac=fac[f].shift().stack().rename(f).reindex(weight_df.index)        
        print('- Write factor stock detail {}'.format(f))
        weight_table=pd.concat([Fac,Industry,Sus,weight_df],axis=1)\
                    .reset_index()\
                    .sort_values(by=['dt','ind',f],ascending=[True,True,False])
        if ind_spc is None:            
            weight_table.to_csv(weight_path+'/weight_{}.csv'.format(f),index=False,float_format='%.5f')
        else:
            weight_table.loc[weight_table['ind']==ind_spc]\
                        .to_csv(weight_path+'/weight_{}.csv'.format(f),index=False,float_format='%.5f')
    return
def output_cash(out_path,Cash,fac):
    if out_path is None:
        return
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    for f in Cash.columns:
        cash_df=Cash[f].unstack(level=0)
        Fac_na=fac[f].shift().isna().mean(axis=1).reindex(cash_df.index).rename(f)
        print('- Write factor cash detail {}'.format(f)) 
        pd.concat([Fac_na,cash_df],axis=1)\
            .reset_index()\
            .to_csv(out_path+'/cash_{}.csv'.format(f),index=False,float_format='%.3f')
    return
        
def run_back_test(data_box,n=5,back_end=None,n_jobs=-1,factor_pool=None,out_path=None,double_side_cost=0,**kwargs):
    '''
    data_box: data box class (compiled)
    n: number of portfolios. p_0 has the largest factor exposure while p_n has the least factor exposure.
    back_end: None/loky/multiprocessing
    factor_pool: subset of factors to run back test
    n_jobs: prossesors to run parallel algorithm. Valid when back end is not None.
    out_path: defualt None. No output. 
    double_side_cost: transaction cost.
    '''
    value_list,turnover_list,weight_list,cash_list=[],[],[],[]
    if back_end is None:
        for f in data_box.Factor.columns.levels[0]:
            print('Process factor {} with single processor'.format(f))
            X=(n,data_box.Price,data_box.Sus,data_box.Ind,data_box.Ind_weight,data_box.Factor.xs(f,axis=1),f,double_side_cost)
            BT_value,BT_turnover,BT_weight,BT_cash=back_test_core(X)
            # BT_value index: portfolio > time. value: values
            # BT_weight index: portfolio > ticker > time  value: weights
            value_list.append(BT_value)
            turnover_list.append(BT_turnover)
            weight_list.append(BT_weight)
            cash_list.append(BT_cash)
    else:
        if back_end is 'loky':
            mul_res=Parallel(n_jobs=n_jobs,**kwargs)(
                    delayed(back_test_core)( (n,data_box.Price,data_box.Sus,data_box.Ind,data_box.Ind_weight,data_box.Factor.xs(f,axis=1),f,double_side_cost)
                                            ) for f in data_box.Factor.columns.levels[0])
        elif back_end is 'multiprocessing':
            X=[(n,data_box.Price,data_box.Sus,data_box.Ind,data_box.Ind_weight,data_box.Factor.xs(f,axis=1),f,double_side_cost) for f in data_box.Factor.columns.levels[0]]
            pool=Pool(processes=n_jobs,**kwargs)            
            mul_res=pool.map(back_test_core,X)
            pool.close()
            pool.join()
        else:
            raise Exception('wrong backend type')
        for res in mul_res:
            value_list.append(res[0])
            turnover_list.append(res[1])
            weight_list.append(res[2])
            cash_list.append(res[3])
            
    Value=pd.concat(value_list,axis=1)
    Turnover=pd.concat(turnover_list,axis=1)
    Cash=pd.concat(cash_list,axis=1)
    Weight=pd.concat(weight_list,axis=1)
    output_weight(Weight,out_path,data_box.Ind,data_box.Ind_weight,data_box.Sus,data_box.Factor)
    output_cash(out_path,Cash,data_box.Factor)
    return Value,Turnover

def run_back_test_by_industry(data_box,industry_list,n=5,back_end=None,n_jobs=-1,factor_pool=None,out_path=None,double_side_cost=0,**kwargs):
    '''
    Run back test in differrent industries.
    '''
    if isinstance(industry_list,list) or isinstance(industry_list,tuple): 
        assert set(industry_list).issubset(data_box.Ind_weight.columns),'industry_list should be contained in data_box.Ind_weight.columns'
    elif industry_list is None:
        industry_list = list(data_box.Ind_weight.columns)
    else:
        raise Exception('Wrong type of industry_list')
    
    value_list,turnover_list,weight_list,cash_list=[],[],[],[]
    if back_end is None:
        for f,ind in itertools.product(data_box.Factor.columns.levels[0],industry_list):
            print('Process factor {} and industry {} with single processor'.format(f,ind))
            X=(n,data_box.Price,data_box.Sus,data_box.Ind               
               ,pd.DataFrame(100,index=data_box.Ind_weight.index,columns=[ind])
               ,data_box.Factor.xs(f,axis=1),f,double_side_cost)
            BT_value,BT_turnover,BT_weight,BT_cash=back_test_core(X)
            # BT_value index: portfolio > time. value: values
            # BT_weight index: portfolio > ticker > time  value: weights
            value_list.append(BT_value)
            turnover_list.append(BT_turnover)
            weight_list.append(BT_weight)
            cash_list.append(BT_cash)
    else:
        if back_end is 'loky':
            mul_res=Parallel(n_jobs=n_jobs,**kwargs)(
                    delayed(back_test_core)( (n,data_box.Price,data_box.Sus,data_box.Ind,pd.DataFrame(100,index=data_box.Ind_weight.index,columns=[ind]),data_box.Factor.xs(f,axis=1),f,double_side_cost)
                                            ) for f,ind in itertools.product(data_box.Factor.columns.levels[0],industry_list))
        elif back_end is 'multiprocessing':
            X=[(n,data_box.Price,data_box.Sus,data_box.Ind,pd.DataFrame(100,index=data_box.Ind_weight.index,columns=[ind]),data_box.Factor.xs(f,axis=1),f,double_side_cost) for f,ind in itertools.product(data_box.Factor.columns.levels[0],industry_list)]
            pool=Pool(processes=n_jobs,**kwargs)            
            mul_res=pool.map(back_test_core,X)
            pool.close()
            pool.join()
        else:
            raise Exception('wrong backend type')
        for res in mul_res:
            value_list.append(res[0])
            turnover_list.append(res[1])
            weight_list.append(res[2])
            cash_list.append(res[3])
    
    m=len(industry_list)
    Value_list,Turnover_list=[],[]
    for ii in range(m):
        ind_name=industry_list[ii]
        Value=pd.concat(value_list[ii::m],axis=1)
        Turnover=pd.concat(turnover_list[ii::m],axis=1)
        Cash=pd.concat(cash_list[ii::m],axis=1)
        Weight=pd.concat(weight_list[ii::m],axis=1)
        if out_path is not None:
            print('Output industry detail {}'.format(ind_name)) 
            output_weight(Weight,out_path+'/industry_{}'.format(ind_name),data_box.Ind,data_box.Ind_weight,data_box.Sus,data_box.Factor,ind_spc=ind_name)
            output_cash(out_path+'/industry_{}'.format(ind_name),Cash,data_box.Factor)
        Value_list.append(Value)
        Turnover_list.append(Turnover)
    return Value_list,Turnover_list