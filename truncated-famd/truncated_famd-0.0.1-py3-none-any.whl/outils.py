# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 17:35:03 2019

@author: luyao.li
"""


import numpy as np
import pandas as pd
from sklearn import preprocessing
from scipy.stats  import pearsonr

class _OneHotEncoder(preprocessing.OneHotEncoder):

    def __init__(self):
        super().__init__(sparse=True, dtype=np.uint8)

    def fit(self, X, y=None):

        self = super().fit(X)
                            
        
        self.column_names_ = self.get_feature_names(X.columns if hasattr( X,'columns') else None)

        return self

    def transform(self, X):
        return pd.SparseDataFrame(
            data=super().transform(X),
            columns=self.column_names_,
            index=X.index if isinstance(X, pd.DataFrame) else None,
            default_fill_value=0
        )
        
        
def _pearsonr(A,B,threshold=0.05):
    co_,p_value=pearsonr(A,B)
    return co_ if p_value <=threshold else  np.nan
