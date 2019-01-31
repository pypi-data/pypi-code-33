# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 10:15:57 2018

@author: yili.peng
"""


import pandas as pd
from .global_func import pre_sus,change_index

class prepare:
    # input d, output dict
    def __init__(self):
        self.dict={}
    def __call__(self,d,ind,vwap,adj,sus,md,inx_weight,**kwarg):
        self.get_factor(d)
        self.get_ind(ind)
        self.get_price(vwap,adj,sus,md)
        self.get_index_weight(inx_weight)
        D = self.integrate()
        return D
    def get_factor(self,d):
        for k,df in d.items():
            self.dict[k]={}
            self.dict[k]['Factor']=change_index(df)
    def get_ind(self,ind):
        self.Industry=change_index(ind)
    def get_price(self,vwap,adj,sus,md):
        self.Price= change_index(vwap * adj)
        self.Suspend= change_index(((sus!=0)|(md!=0)).astype(int).mask((sus.isna())|(md.isna())).apply(pre_sus))
    def get_index_weight(self,inx_weight):
        self.Index_weight=change_index(inx_weight)
    def integrate(self):
        self.Industry_Weight=pd.concat([self.Index_weight,self.Industry],axis=1,keys=['weight','ind']).stack(dropna=False).fillna(0).groupby(['dt','ind']).aggregate(sum)['weight'].unstack()
        for k,d in self.dict.items():            
            inter_tickers=list(set(d['Factor'].columns) & set(self.Price.columns) & set(self.Suspend.columns) & set(self.Industry.columns) )
            inter_time=list(set(d['Factor'].index) & set(self.Price.index) & set(self.Suspend.index) & set(self.Industry.index) & set(self.Industry_Weight.index))
            inter_tickers.sort()
            inter_time.sort()
            self.dict[k]['Factor']=d['Factor'].loc[inter_time,inter_tickers]
            self.dict[k]['Price']=self.Price.loc[inter_time,inter_tickers]
            self.dict[k]['Suspend']=self.Suspend.loc[inter_time,inter_tickers]
            self.dict[k]['Industry']=self.Industry.loc[inter_time,inter_tickers]
            self.dict[k]['Industry_Weight']=self.Industry_Weight.loc[inter_time]
        return self.dict
