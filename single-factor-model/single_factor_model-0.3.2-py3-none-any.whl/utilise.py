# -*- coding: utf-8 -*-
"""
Created on Tue May  8 13:30:40 2018

@author: yili.peng
"""

import pandas as pd
import numpy as np
from numba import jit

@jit(nopython=True)
def seperate_core(k,n):
    a=k/float(n)
    b=1
    lst=[]
    lst2=[]
    for i in range(k+n-1):
        if b<=a:
            a-=b
            lst.append(b)
            b=1
        else:
            lst.append(a)
            b-=a
            a=k/float(n)
            lst2.append(i+1)
    return lst,lst2

@jit(nopython=True)
def seperate_core2(k,n):
    weights_st=np.zeros(shape=(n,k))
    lst,lst2=seperate_core(k,n)
    lst3=[0]+lst2+[len(lst)]
    l=0
    for i in range(n):
        for j in range(lst3[i],lst3[i+1]):
            weights_st[i,l]=lst[j]
            l+=1
        l-=1
    return weights_st

def seperate(l,n):
    k=len(l)
    if k==1:
        return pd.DataFrame([1.0]*n,columns=l,index=range(n))    
    weights_st=pd.DataFrame(seperate_core2(k,n),columns=l,index=range(n))
    return weights_st.div(weights_st.sum(axis=1),axis=0)
