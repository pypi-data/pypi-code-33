# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 14:43:42 2019

@author: luyao
"""

from .base import  _BasePCA


from math import log
from scipy.sparse  import issparse
from scipy.sparse.linalg import svds 
from scipy import linalg
from scipy.special import gammaln

from sklearn.utils import check_array,check_random_state

from sklearn.utils.extmath import _incremental_mean_and_var,svd_flip,stable_cumsum,randomized_svd
from sklearn.utils.sparsefuncs_fast import  incr_mean_variance_axis0
from  sklearn.utils import gen_batches

import numpy as np
import pandas as pd
import numbers
import six

from .outils import _pearsonr

from sklearn.preprocessing import  StandardScaler
from sklearn.exceptions import DataConversionWarning
import warnings
warnings.filterwarnings("ignore",category=DataConversionWarning)

    
def _assess_dimension_(spectrum, rank, n_samples, n_features):
    """Compute the likelihood of a rank ``rank`` dataset
    The dataset is assumed to be embedded in gaussian noise of shape(n,
    dimf) having spectrum ``spectrum``.
    Parameters
    ----------
    spectrum : array of shape (n)
        Data spectrum.
    rank : int
        Tested rank value.
    n_samples : int
        Number of samples.
    n_features : int
        Number of features.
    Returns
    -------
    ll : float,
        The log-likelihood
    Notes
    -----
    This implements the method of `Thomas P. Minka:
    Automatic Choice of Dimensionality for PCA. NIPS 2000: 598-604`
    """
    if rank > len(spectrum):
        raise ValueError("The tested rank cannot exceed the rank of the"
                         " dataset")

    pu = -rank * log(2.)
    for i in range(rank):
        pu += (gammaln((n_features - i) / 2.) -
               log(np.pi) * (n_features - i) / 2.)

    pl = np.sum(np.log(spectrum[:rank]))
    pl = -pl * n_samples / 2.

    if rank == n_features:
        pv = 0
        v = 1
    else:
        v = np.sum(spectrum[rank:]) / (n_features - rank)
        pv = -np.log(v) * n_samples * (n_features - rank) / 2.

    m = n_features * rank - rank * (rank + 1.) / 2.
    pp = log(2. * np.pi) * (m + rank + 1.) / 2.

    pa = 0.
    spectrum_ = spectrum.copy()
    spectrum_[rank:n_features] = v
    for i in range(rank):
        for j in range(i + 1, len(spectrum)):
            pa += log((spectrum[i] - spectrum[j]) *
                      (1. / spectrum_[j] - 1. / spectrum_[i])) + log(n_samples)

    ll = pu + pl + pv + pp - pa / 2. - rank * log(n_samples) / 2.

    return ll


def _infer_dimension_(spectrum, n_samples, n_features):
    """Infers the dimension of a dataset of shape (n_samples, n_features)
    The dataset is described by its spectrum `spectrum`.
    """
    n_spectrum = len(spectrum)
    ll = np.empty(n_spectrum)
    for rank in range(n_spectrum):
        ll[rank] = _assess_dimension_(spectrum, rank, n_samples, n_features)
    return ll.argmax()


class  PCA(_BasePCA):
    def __init__(self,standard_scaler=True,n_components=2,svd_solver='auto',whiten=False,copy=True,
                 tol=None,iterated_power=2,batch_size =None,random_state=None):
        '''
#    standard_scaler:True
#    n_components:int
#    svd_solver: str  if X is sparse array,->{'arpack','randomized'}
#    whiten:Bool false
#    copy:Bool  True
#    
#    random_state:
#    tol: in  scipy,sparse.linalg.svds
#    iterated_power :'auto', sklearn.utils.extmath.randomized_svd 
#    batch_size:  in  partial_fit,truncated_svd
        ''' 
        for k,v in locals().items():
            if k!='self':
                setattr(self,k,v)
    
    def  fit(self,X,y=None):
        
        if  isinstance(X,(pd.DataFrame,pd.SparseDataFrame)):
            X=X.values

            
        self._fit(X)
        return self
    
    def _fit(self,X,y=None):
        try:
            check_array(X,accept_sparse=['csc','csr'])
        except Exception:
            raise ValueError('{0}'.format(X[:10000,1]) ,X.shape)
        n_samples,n_features =X.shape
        
        if  n_features >= n_samples:
            raise ValueError('input array  n_features >= n_samples')
            
        if  self.standard_scaler:
            self.scaler_=StandardScaler(copy=self.copy)
            X= self.scaler_.fit_transform(X)
            
        self.mean_=0.
        self.var_ =0.
        self.n_sample_seen=0
        self.components_=None
        self.explained_variance_=None
        self.explained_variance_ratio_=None
        self.singular_values = None
        self.noise_variance = None
        
        
        #determine  batch_size
        if  self.batch_size is None:
            batch_size = 3 * n_features
        else:
            batch_size =self.batch_size
        
        #determine n_components
        if self.n_components is None:
            if  self.svd_solver != 'arpack':
                n_components =min(n_samples,n_features)
            else:
                n_components = min(n_samples,n_features) -1
        else:
            n_components =self.n_components
        
        self.n_components= n_components
        
        #determine  svd_solver
        _fit_svd_solver= self.svd_solver
        if _fit_svd_solver == 'auto':
            if  max(n_samples,n_features)<=500 or  n_components=='mle':
                _fit_svd_solver='full'
            elif 1<= n_components <   0.8 * min(n_samples,n_features):
                _fit_svd_solver='randomized'
            else:
                _fit_svd_solver ='full'

        

        if  issparse(X) and _fit_svd_solver not in  ['arpack','randomized']:
            raise ValueError('while  X is sparse matrix,svd_solver must be choosen between {arpack, randomized} not {0}'.format(_fit_svd_solver))
        
        for  s in   gen_batches(n_samples,batch_size,
                                min_batch_size=self.components_ or 0):
            U,S,VT= self.partial_fit(X[s],check_input=False,svd_solver=_fit_svd_solver)
        return  U,S,VT
    
    def partial_fit(self,X ,y=None,check_input=True,svd_solver ='auto'):
        '''
        incremental_PCA 
        if svd_solver  in ['arpack','randomized'] -> _fit_truncated
        elif svd_solver == 'full'  -> _fit_full
        else: raise ValueError

#    standard_scaler:True
#    whiten:Bool false
#    copy:Bool  True
#    除开直接从_init__ 继承过来的attr ,其他必需attr or  None attr 都需要考虑 components_,n_components,svd_solver

        '''
        if check_input:
            check_array(X,copy=self.copy,accept_sparse=['csc','csr'])
        
        n_samples,n_features=  X.shape
        
        '''
        partial_fit: directly 
        '''
        if self.standard_scaler:
            if not hasattr(self,'scaler_'):
                self.scaler_ = StandardScaler()
                X=self.scaler_.fit_transform(X)
        
        
        if not hasattr(self,'components_'):
            self.components_ =None
        
        #determine  n_components
        if self.n_components is None:  #n_component -> n_components
            if  self.components is None:
                if  self.svd_solver != 'arpack':
                    n_components =min(n_samples,n_features)
                else:
                    n_components = min(n_samples,n_features) -1
            else:
                n_components= self.components_.shape[0]
        else:
            n_components=self.n_components  # ->  _partial_fit_full,_partial_fit_truncated  process the case where  n_components  in [0,1] ,'mle',int
            
        
        self.n_components = n_components
        
        _fit_svd_solver= self.svd_solver
        if _fit_svd_solver == 'auto':
            if  max(n_samples,n_features)<=500 or  n_components=='mle':
                _fit_svd_solver='full'
            elif 1<= n_components <   0.8 * min(n_samples,n_features):
                _fit_svd_solver='randomized'
            else:
                _fit_svd_solver ='full'
                
        if self.components_ is not None and  n_components != self.components_.shape[0]:
            raise ValueError( 'n_components  should be identical with  components_')
        
        
        #Beginning step
        if not hasattr(self ,'n_sample_seen'):
            self.n_sample_seen =0
            self.mean_ =0.
            self.var_ = 0.
        
        '''
        '''
        if issparse(X) :
            total_mean,total_variance,n_sample_total=incr_mean_variance_axis0(X,self.mean_,self.var_,self.n_sample_seen)
        
            
        else:
            total_mean,total_variance,n_sample_total=_incremental_mean_and_var(X,self.mean_,self.var_,self.n_sample_seen)
        
        n_sample_total=n_sample_total[0]
        if  self.n_sample_seen == 0 :
            X = X- total_mean
        else:
            _local_mean= np.mean(X,axis=0)\
            
            X =X - _local_mean
            #mean_correction= sqrt( local_samples*merge_before_samples/merge_after_samples )*(merge_before_mean-local_mean )
            mean_correction=np.sqrt( (n_samples*self.n_sample_seen )/n_sample_total)*(self.mean_ - _local_mean )
            #vstack : singular_values_(K,)*components_(K,N),X(M,N),mean_correction(N,)
            X=np.vstack((self.singular_values[:,None]*self.components_,X,mean_correction))
          
        self.mean_ = total_mean
        self.var_ = total_variance
        self.n_sample_seen = n_sample_total
        
        if _fit_svd_solver  == 'full': 
            return self._partial_fit_full(X)
        elif _fit_svd_solver in ['arpack','randomized']:
            return  self._partial_fit_truncated(X,_fit_svd_solver)
        else:
            raise ValueError("svd_solver:{0} not exits in {'full','randomized','arpack','auto'}".format(_fit_svd_solver))


    
    def  _partial_fit_full(self ,X) :
        '''
        n_components=[ 0,1] ,int >=1 ,'mle'
        Consider the follow cases:
            1. n_components =='mle',n_samples < n_features
            2.n_components !='mle',not  0 <=n_components <= min(X.shape)
            3.n_components !='mle',n_components  >=1,not  isinstance(n_components,numbers.Integral,np.integer)
        
        using  scipy.linalg.svd(X,full_matrics=False)
        '''
        n_samples,n_features =X.shape
        if self.n_components =='mle':
            if n_samples < n_features:
                raise ValueError(' n_samples{0} < n_features{1}'.format(n_samples,n_features))
        elif not  0 <=self.n_components <= min(n_samples,n_features):
            raise ValueError('N_Components {0} not beween 0 and min(n_samples,n_features)'.format(self.n_components) )
        elif self.n_components >=1:
            if not isinstance(self.n_components ,(numbers.Integral,np.integer)):
                raise ValueError('Since n_components >=1,its dtype must be integer')
                
        U,S,VT=linalg.svd(X,full_matrices=False)
        U,VT=svd_flip(U,VT)
        
        components_= VT
        explained_variance_= S**2/(n_samples -1)
        if hasattr(self,'total_var'):
            total_var=self.total_var
        else:
            total_var=  explained_variance_.sum()
        explained_variance_ratio_=  explained_variance_/ total_var
        singular_values=S.copy()
        
        
        if self.n_components =='mle':
            n_components =_infer_dimension_(X,n_samples,n_features)
        elif 0.0 < self.n_components < 1.0:
            cumsum_explained_var_=stable_cumsum(explained_variance_ratio_)
            n_components =np.searchsorted(cumsum_explained_var_,self.n_components)+1
        else:
            n_components=self.n_components
    
        
        self.n_components = n_components
        
        self.components_=components_[:self.n_components]
        self.explained_variance_ =explained_variance_[:self.n_components]
        self.explained_variance_ratio_= explained_variance_ratio_[:self.n_components] 
        self.singular_values =singular_values[:self.n_components]
        
        if n_components <  min(n_samples,n_features):
            self.noise_variance =explained_variance_[self.n_components:].mean()
        else:
            self.noise_variance=0.0
        
        return U,S,VT

    
    def  _partial_fit_truncated(self ,X,svd_solver=None) :
        '''
        n_components=int 
        Consider the follow cases:
            1. not isinstance(n_components,six.string_types )
            2.not  1 <=n_components <= min(X.shape)
            3.not  isinstance(n_components,numbers.Integral,np.integer)  
            4.svd_solver='arpack',n_components =min(X.shape)
        '''
        random_state=check_random_state(self.random_state)
        
        n_samples,n_features =X.shape
        if isinstance(self.n_components,six.string_types):
            raise ValueError('N_components dtypes should not be string types')
        
        elif not  1<=self.n_components <= min(n_samples,n_features):
            raise  ValueError('n_components:{0}  not between 1 and {1}'.format(self.n_components,min(n_samples,n_features)))
        
        elif not isinstance(self.n_components,(numbers.Integral,np.integer)):
            raise  ValueError('n_components:{0} must be type integer '.format(self.n_components))
            
        elif svd_solver =='arpack' and  self.n_components == min(n_samples,n_features):
            raise ValueError("n_components:%r should be less than %r while svd_solver =='arpack'"%(self.n_components,min(n_samples,n_features)))
        
        if svd_solver =='arpack':
            v0=random_state.uniform(-1,1,size=min(n_samples,n_features))
            U,S,VT= svds(X,k=self.n_components,tol=self.tol,v0=v0)
            S=S[::-1]
            U,VT=svd_flip(U[::-1],VT[::-1])
        else:
            U,S,VT=randomized_svd(X,n_components=self.n_components,
                                  n_iter=self.iterated_power,
                                  flip_sign=True,
                                  random_state=random_state)
                   
        self.components_= VT
        self.explained_variance_= S**2/(n_samples -1)
        
        if hasattr(self,'total_var'):
            total_var=self.total_var  #MCA :float
        else:
            total_var=  np.var(X,ddof=1,axis=0).sum()
        self.explained_variance_ratio_=  self.explained_variance_/ total_var
        self.singular_values=S.copy()        
        
        if self.n_components <  min(n_samples,n_features):
            self.noise_variance =(total_var - self.explained_variance_.sum())/(min(n_samples,n_features)-self.n_components) 
        else:
            self.noise_variance=0.
        
        
        return U,S,VT
    
    def fit_transform(self, X,y=None):
        n_samples,n_features= X.shape
        
        if  isinstance(X,(pd.DataFrame,pd.SparseDataFrame)):
            X=X.values   
            
        U,S,VT=self._fit(X)

        U=U[:,:self.n_components]
        if self.whiten:
            U*=np.sqrt(n_samples -1)
        else:
            U*=S[:self.n_components]
        
        return U 
    
    def column_correlation(self,X,same_input=True):
        #same_input: input for fit process is the same with that of X
        # self.components_  and outer array  X
        #co
        if   isinstance(X,pd.DataFrame):
            col_names=X.columns
            X=X.values        
        else:
            col_names=np.arange(X.shape[1])
        
        if   same_input: #X is fitted and the the data fitting and the data transforming is the same
            X_t=self.transform(X)
        else:
            X_t=self.fit_transform(X)

        return  pd.DataFrame({index_comp:{ 
                                        col_name: _pearsonr(X_t[:,index_comp],X[:,index_col])
                                          for index_col,col_name in enumerate(col_names)  
                                                }
                                                for index_comp  in range(X_t.shape[1])})
        
    
    
    


        

                
        
            
        
        
        
        
    
        
        
        
                
        
        
        
        
        
        
        
        
        
        
            
        
        
        
        
            
        
        
            

            
        
        
        
        
        
        
        
        
        
        
        
        
        
        