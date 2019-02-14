# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 17:15:08 2019

@author: luyao.li
"""

""" Factor Analysis of Mixed Data Base Classes"""
from abc import ABCMeta,abstractmethod
from scipy import linalg

import numpy as np 
import six

from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.utils import check_array
from sklearn.utils.validation import  check_is_fitted
from sklearn.utils.extmath import  safe_sparse_dot


@six.add_metaclass(ABCMeta)
class _BasePCA(BaseEstimator,TransformerMixin): 
    
    def get_convariance(self):
        """Compute data covariance with the generative model.
        ``cov = components_.T * S**2 * components_ + sigma2 * eye(n_features)``
        where  S**2 contains the explained variances, and sigma2 contains the
        noise variances.
        Returns
        -------
        cov : array, shape=(n_features, n_features)
            Estimated covariance of data.
        """
        components_ = self.components_
        exp_var = self.explained_variance_
        if self.whiten:
            components_ = components_ * np.sqrt(exp_var[:, np.newaxis])
        exp_var_diff = np.maximum(exp_var - self.noise_variance_, 0.)
        cov = np.dot(components_.T * exp_var_diff, components_)
        cov.flat[::len(cov) + 1] += self.noise_variance_ 
        return cov
    
    def  get_precision(self):
        """Compute data precision matrix with the generative model.
        Equals the inverse of the covariance but computed with
        the matrix inversion lemma for efficiency.
        Returns
        -------
        precision : array, shape=(n_features, n_features)
            Estimated precision of data.
        """
        n_features = self.components_.shape[1]

        # handle corner cases first
        if self.n_components_ == 0:
            return np.eye(n_features) / self.noise_variance_
        if self.n_components_ == n_features:
            return linalg.inv(self.get_covariance())

        # Get precision using matrix inversion lemma
        components_ = self.components_
        exp_var = self.explained_variance_
        if self.whiten:
            components_ = components_ * np.sqrt(exp_var[:, np.newaxis])
        exp_var_diff = np.maximum(exp_var - self.noise_variance_, 0.)
        precision = np.dot(components_, components_.T) / self.noise_variance_
        precision.flat[::len(precision) + 1] += 1. / exp_var_diff
        precision = np.dot(components_.T,
                           np.dot(linalg.inv(precision), components_))
        precision /= -(self.noise_variance_ ** 2)
        precision.flat[::len(precision) + 1] += 1. / self.noise_variance_
        return precision
    
    
    @abstractmethod
    def fit(self,X,y=None):
        """Placeholder for fit. Subclasses should implement this method!
        Fit the model with X.
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data, where n_samples is the number of samples and
            n_features is the number of features.
        Returns
        -------
        self : object
            Returns the instance itself.
        """
    def transform(self,X):
        
        check_is_fitted(self,['mean_','components_'])
        check_array( X,accept_sparse=['csr','csc'])
        
        
        if  hasattr(self,'scaler_'):
            X=self.scaler_.transform(X,copy=self.copy)
        
        X_t=safe_sparse_dot(X,self.components_.T)
        
        if self.whiten:
            X_t/= np.sqrt( self.explained_variance_)  #1.
            
        return  X_t

    def invert_transform(self,X):
        '''
        if whiten: X_raw= X* np.sqrt(explained_variance_) @ components
        else:  X_raw =X @ components
        '''
        if self.whiten:
            X *=np.sqrt( self.explained_variance_)
        return  safe_sparse_dot(X,self.components_)
    

        
        
        
    
    
    
    
    
    
    