# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 10:39:04 2019

@author: luyao.li
"""

from .fast_MFA  import MFA
import pandas as pd
import numpy as np

class  FAMD(MFA):
    def __init__(self,n_components=2,svd_solver='auto',copy=True,
             tol=None,iterated_power=2,batch_size =None,random_state=None):
        super().__init__(
                         n_components=n_components,
                         svd_solver=svd_solver,
                         copy=copy,
                         tol=tol,
                         iterated_power=iterated_power,
                         batch_size =batch_size,
                         random_state=random_state)   
    
    def fit(self,X,y=None):
        if not isinstance(X,(pd.DataFrame,pd.SparseDataFrame)):
            X=pd.DataFrame(X) 
        _numric_columns= X.select_dtypes(include=np.number).columns
        _category_columns=X .select_dtypes(include=['object','category']).columns
        self.groups= {'Numerical':_numric_columns ,'Categorical':_category_columns }
        
        return  super().fit(X)
    
    def fit_transform(self,X,y=None):
        self.fit(X)
        return  self.transform(X)
