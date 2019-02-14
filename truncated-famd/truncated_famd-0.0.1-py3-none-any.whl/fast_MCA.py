# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 11:31:55 2019

@author: luyao.li
"""

from  .fast_PCA import PCA
import numpy as np
import pandas as pd

from scipy.sparse import diags,issparse

from sklearn.utils import check_array
from sklearn.utils.validation import check_is_fitted
from sklearn.utils.extmath import safe_sparse_dot

from .outils import  _OneHotEncoder,_pearsonr




class CA(PCA):
    def __init__(self,n_components=2,svd_solver='auto',copy=True,
                 tol=None,iterated_power=2,batch_size =None,random_state=None):
        super().__init__(
                        standard_scaler=False,
                         n_components=n_components,
                         svd_solver=svd_solver,
                         whiten=False,
                         copy=copy,
                         tol=tol,
                         iterated_power=iterated_power,
                         batch_size =batch_size,
                         random_state=random_state)
        
    def fit(self, X,y=None):

        
        if  isinstance(X,(pd.DataFrame,pd.SparseDataFrame)):
            X=X.values
        if np.any(X<0,axis=None):
            raise ValueError('All values in X must be positive')

        X = X/np.sum(X)
        
        #compute row and column masses
        self.r_=  np.sum(X,axis=1)
        self.c_= np.sum(X,axis=0)

        if issparse(X):
            _S=safe_sparse_dot(diags(self.r_ ** -0.5).toarray(),X- np.outer(self.r_,self.c_) )
            S=safe_sparse_dot(_S,diags(self.c_** -0.5).toarray())
        else:
            S=diags(self.r_ ** -0.5) @ (X- np.outer(self.r_,self.c_) ) @ diags(self.c_** -0.5)

        self= super().fit(S)
        
        return self
    
    def transform(self,X):
        if  isinstance(X,(pd.DataFrame,pd.SparseDataFrame)):
            X=X.values
            
        check_is_fitted(self,['mean_','components_'],all_or_any=all)
        check_array(X)   
        
        X =X/ np.sum(X,axis=1)[:,None]
        
        if issparse(X):
            _X=safe_sparse_dot(X,diags(self.c_ ** - 0.5) )
            X_t=safe_sparse_dot(_X,self.components_.T)
        else:
            X_t= X @ diags(self.c_ ** -0.5) @ self.components_.T
                    
        return  X_t       
    
    def fit_transform(self,X):
        self.fit(X)
        return self.transform(X)



class MCA(CA):
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
            
        def  fit(self,X,y=None):
            
            n_initial_cols=X.shape[1]
            self.one_hot=_OneHotEncoder().fit(X)
            n_new_cols=len(self.one_hot.column_names_)
            self.total_var = (n_new_cols-n_initial_cols) / n_initial_cols
            return super().fit(self.one_hot.transform(X))
             
        def transform(self,X,y=None):
            return super().transform( self.one_hot.transform(X))
        
        
        def column_correlation(self,X,same_input=True):
            if   same_input: #X is fitted and the the data fitting and the data transforming is the same
                X_t=self.transform(X)
            else:
                X_t=self.fit_transform(X)
   
            X_one_hot =self.one_hot.transform(X)
            
            return pd.DataFrame({index_comp:{ 
                                col_name: _pearsonr(X_t[:,index_comp],X_one_hot.loc[:,col_name].values.to_dense())
                                  for col_name in  X_one_hot
                                        }
                                        for index_comp  in range(X_t.shape[1])})
                    
        

