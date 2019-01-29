# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 10:43:30 2019

@author: yili.peng
"""

from .utilise import pre_sus,change_index,monthmove,check_time,easy_regression,ci_transformer,timeit
from datetime import datetime
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
import pickle

class data_box(object):
    def __init__(self):
        self._factorDF=None
        self._freq='d'
        self._day_lag=0
        self._period_lag=0
        self._fixed_date=None
        self._start_time=None
        self._end_time=None
        
        self._Factors={}
        self._cap=None
        self._suspend=None
        self._price=None
        self._industry=None
        self._industry_weight=None
        self._index_weight=None
        self._factorDF=None

    @property
    def Price(self):
        assert self._price is not None,'Load Price first'
        return self._price.loc[self._start_time:self._end_time]
    @property
    def Sus(self):
        assert self._suspend is not None,'Load Suspend first'
        return self._suspend.loc[self._start_time:self._end_time]
    @property
    def Ind(self):
        assert self._industry is not None,'Load Industry first'
        return self._industry.loc[self._start_time:self._end_time]
    @property
    def Ind_weight(self):
        assert self._industry_weight  is not None,'Load IndustryWeight first or load IndexWeight and Industry and calc_indweight'
        return self._industry_weight.loc[self._start_time:self._end_time]
    @property
    def Index_weight(self):
        assert self._index_weight is not None,'Load IndexWeight first'
        return self._index_weight.loc[self._start_time:self._end_time]
    @property
    def Cap(self):
        assert self._cap is not None,'Load Cap first'
        return self._cap.loc[self._start_time:self._end_time]
    @property
    def Factor(self):
        if self._factorDF is None:
            assert len(self._Factors) is not 0,'Load Factor first'
            return pd.concat(self._Factors.values(),axis=1,keys=self._Factors.keys()).loc[self._start_time:self._end_time]
        else:
            return self._factorDF.loc[self._start_time:self._end_time].rename_axis('dt').rename_axis([None,'ticker'],axis=1)
    
    def set_lag(self,freq='d',period_lag=0,day_lag=0,fixed_date=None):
        '''
        freq: 'd'/'m' daily or monthly
        day_lag: int
            Lags between the factor exposure date (T) and the factor exposure calculated date (T+n).
            lag = 0 means factor can be used T+1 
        period_lag: int
            Lags between the factor exposure period (T) and the factor exposure calculated period (T+n)
            For freq='d', period_lag and  day_lag are the same, the max of these two would be used.
            But for freq='m', total lag is the plus of day_lag and period_lag
        fixed_date: int
            Fixed calulate date when freq = 'm', combined with period_lag and day_lag if set.
        '''
        
        assert freq.lower() in ('d','m'), 'freq must in "d" / "m"'
        assert (fixed_date is None) or (type(fixed_date) is int), 'fixed_date must be None or int'
        
        self._freq=freq
        if freq is 'd':
            self._day_lag=self._period_lag=max(period_lag,day_lag)
        else:
            self._day_lag=day_lag
            self._period_lag=period_lag
            self._fixed_date=fixed_date
        return self
    def set_time(self,start_time=None,end_time=None):
        '''  
        set time span
        '''
        self._start_time=(datetime.strptime(str(start_time),'%Y%m%d') if start_time is not None else None)
        self._end_time=(datetime.strptime(str(end_time),'%Y%m%d') if end_time is not None else None)
        return self
    def add_factor(self,factor_name,factor_df,change_index_to_date=True,date_type='%Y%m%d',factor_pool=None):
        '''
        factor_name: str
        factor_df: DataFrame (times*tickers). Monthly factor should be have only one index each month
        factor_pool: Pool of factors to be included. Default None (all)
        '''
        if (factor_pool is None) or (factor_name in factor_pool):
            assert factor_df.apply(is_numeric_dtype).all(), 'Factor DataFrame contains Non-numeric type'
            self._Factors[factor_name]=(change_index(factor_df,date_type='%Y%m%d') if change_index_to_date else factor_df)
        return self
    def load_adjPrice(self,price_df,change_index_to_date=True,date_type='%Y%m%d'):
        
        assert price_df.apply(is_numeric_dtype).all(), 'Open DataFrame contains Non-numeric type'
        self._price=(change_index(price_df,date_type) if change_index_to_date else price_df)
        return self
    def load_suspend(self,suspend_df,change_index_to_date=True,date_type='%Y%m%d'):
        
        assert suspend_df.apply(is_numeric_dtype).all(), 'Suspend DataFrame contains Non-numeric type'
        suspend_df2=suspend_df.astype(int).apply(pre_sus)
        self._suspend=(change_index(suspend_df2,date_type) if change_index_to_date else suspend_df2)
        return self
    def load_indestry(self,industry_df,change_index_to_date=True,date_type='%Y%m%d',mapping=False):
        '''
        industry_df: pd.Dataframe
        '''
        if mapping:
            stacked=industry_df.stack()
            lst=stacked.unique()
            mapping=pd.Series(range(len(lst)),index=lst)
            industry_df=pd.Series(mapping.reindex(stacked).values,index=stacked.index).unstack()
            
        assert industry_df.apply(is_numeric_dtype).all(), 'Industry DataFrame contains Non-numeric type'
        self._industry = (change_index(industry_df,date_type) if change_index_to_date else industry_df)
        return self
    def load_indexWeight(self,index_weight_df,change_index_to_date=True,date_type='%Y%m%d'):
        
        assert index_weight_df.apply(is_numeric_dtype).all(), 'Index Weight DataFrame contains Non-numeric type'
        self._index_weight = (change_index(index_weight_df,date_type) if change_index_to_date else index_weight_df)
        return self
    def load_cap(self,cap_df,change_index_to_date=True,date_type='%Y%m%d'):
        assert cap_df.apply(is_numeric_dtype).all(), 'Cap DataFrame contains Non-numeric type'
        self._cap = (change_index(cap_df,date_type) if change_index_to_date else cap_df)
        return self
    
    def load_indWeight(self,ind_weight_df,change_index_to_date=True,date_type='%Y%m%d'):
        assert ind_weight_df.apply(is_numeric_dtype).all(), 'Ind Weight DataFrame contains Non-numeric type'
        self._industry_weight = (change_index(ind_weight_df,date_type) if change_index_to_date else ind_weight_df)
        return self
    
    @timeit
    def calc_indweight(self):
        self._industry_weight=pd.concat([self._index_weight,self._industry],axis=1,keys=['weight','ind']).stack(dropna=False).fillna(0).groupby(['dt','ind']).aggregate(sum)['weight'].unstack()
        return self
    @timeit
    def align_data(self):
        '''
        This process would align tickers and time for all data.
        '''
        assert len(self._Factors)>0,'load factor first'
        
        CI=ci_transformer()
        
        #columns
        CI.fit_columns(self._industry,self._suspend,self._price,self._cap,self.Factor.stack(dropna=False,level=0))
        self._industry,self._suspend,self._price,self._cap,factors =  CI.transform_columns(self._industry,self._suspend,self._price,self._cap,self.Factor.stack(dropna=False,level=0))        
        if self._freq=='d':
            # daily
            CI.fit_index(self._price,self._suspend,self._cap,self._industry,self._index_weight,self._industry_weight)
            # transform
            self._price,self._suspend,self._cap,self._industry,self._index_weight,self._industry_weight,factors2 = CI.transform_index(self._price,self._suspend,self._cap,self._industry,self._index_weight,self._industry_weight,factors.unstack())            
            self._factorDF=factors2.shift(self._day_lag)\
                                    .swaplevel(axis=1)\
                                    .sort_index(axis=1)
            # clean
            factors=factors2=None            
        elif self._freq=='m':
            # monthly
            # Monthly factor should be have only one index each month            
            CI.fit_index(self._price,self._suspend,self._cap,self._industry,self._index_weight,self._industry_weight)
            trading_calendar=CI.index
            factors2=factors.unstack().shift(self._period_lag)
            lst = [int(i.strftime('%Y%m%d')[:6]) for i in factors2.index]             
            assert len(set(lst)) == len(lst), 'Monthly factor have a invalid frequency'                       
            if self._fixed_date is None:
                # no fixed date
                # change index                           
                new_index=pd.DataFrame([[i,int(i.strftime('%Y%m%d')[:6])] for i in trading_calendar],columns=['dt','ym'])\
                                .groupby('ym').agg({'dt':max})['dt']\
                                .reindex(lst).values
                factors3=factors2.assign(dt=new_index)\
                        .loc[~pd.Series(new_index).isna().values]\
                        .set_index('dt')
            else:
                # fixed date
                target_lst=[check_time(monthmove(l)+str(self._fixed_date).zfill(2)) for l in lst]
                new_index=[pd.Series(trading_calendar).loc[pd.Series(trading_calendar).le(l)].max() for l in target_lst]
                factors3=factors2.assign(dt=new_index)\
                        .loc[~pd.Series(new_index).eq(pd.Series(new_index).shift()).values]\
                        .set_index('dt')

            # transform
            self._price,self._suspend,self._cap,self._industry,self._index_weight,self._industry_weight,factors4 = CI.transform_index(self._price,self._suspend,self._cap,self._industry,self._index_weight,self._industry_weight,factors3)
            self._factorDF=factors4.shift(self._day_lag)\
                                    .swaplevel(axis=1)\
                                    .sort_index(axis=1)

            # clean
            factors=factors2=factors3=factors4=None
        return self
    @timeit
    def factor_ind_neutral(self):
        grouped=pd.concat([self.Factor.stack(),self.Ind.stack().rename('_ind')],axis=1).groupby(['dt','_ind'])
        self._factorDF=self.Factor-grouped.transform(np.mean).unstack()
        return self
    @timeit    
    def factor_size_neutral(self,ln=False,ind_neutral_size=False):
        size=np.log(self.Cap) if ln else self.Cap
        cap_grouped=size.stack().rename('size').to_frame().groupby('dt') if not ind_neutral_size else pd.concat([size.stack().rename('size'),self.Ind.stack().rename('_ind')],axis=1).groupby(['dt','_ind'])
        cap_zscore=(size-cap_grouped.transform(np.mean)['size'].unstack())/cap_grouped.transform(np.std,ddof=1)['size'].unstack()
        new_factor_list=[]
        for dt in self.Factor.index:
            sub_factor=self.Factor.loc[dt]
            for k in self._Factors.keys():
                sample=pd.concat([cap_zscore.loc[dt].rename('size'),sub_factor.loc[k].rename('factor')],axis=1).dropna()
                if sample.shape[0]<0:
                    new_factor_list.append(pd.Series(name=(dt,k)))
                else:
                    s,f=sample['size'],sample['factor']
                    new_factor_list.append(easy_regression(f,s).rename((dt,k)))
        self._factorDF=pd.concat(new_factor_list,axis=1).stack(level=0).unstack(level=0)
        return self
    @timeit    
    def factor_zscore(self,method='std'):
        '''
        method=std/leverage (i.e. l2-norm / l1-norm)
        '''
        grouped=self.Factor.stack().groupby('dt')
        if method=='std':
            self._factorDF=(self.Factor-grouped.transform(np.mean).unstack())/grouped.transform(np.std,ddof=1).unstack()
        elif method=='leverage':
            self._factorDF=(self.Factor-grouped.transform(np.mean).unstack())/grouped.transform(lambda x: np.sum(np.abs(x))).unstack()
        else:
            print('method should be "std" or "leverage"')
        return self
    @timeit
    def factor_pca(self,n=None,na_thresh=0.2):
        '''
        Pca adjust for all factors. Missing values are filled with mean before processing.
        '''
        try:
            from sklearn.decomposition import PCA
            from sklearn.preprocessing import Imputer
        except:
            print('sklearn is needed for factor_pca')
            return self
        n=len(self.Factor.columns.levels[0]) if n is None else n
        f_list=[]
        for dt in self.Factor.index:
            sub_factor=self.Factor.loc[dt].unstack().T
            sub_factor=sub_factor.loc[:,sub_factor.isna().mean().le(na_thresh)]
            if sub_factor.shape[1]>0:
                m=min(n,sub_factor.shape[1])
                X=Imputer(strategy='median').fit_transform(sub_factor)
                X_new=PCA(n_components=m).fit_transform(X)
                f_list.append(pd.DataFrame(X_new,index=sub_factor.index,columns=['Factor_Pca_{}'.format(i) for i in range(m)]).unstack().rename(dt))
            else:
                f_list.append(pd.DataFrame(np.nan,index=sub_factor.index,columns=['Factor_Pca_{}'.format(i) for i in range(n)]).unstack().rename(dt))
        self._factorDF=pd.concat(f_list,axis=1).T
        return self
    @timeit
    def clean_factor(self):
        self._factorDF=None
        self._Factors={}
        return self
    @timeit
    def save(self,path):
        with open(path,'wb') as f:
            f.write(pickle.dumps(self.__dict__))
        return self
    @timeit
    def load(self,path):
        with open(path,'rb') as f:
            dataPickle = f.read()
        self.__dict__=pickle.loads(dataPickle)
        return self

