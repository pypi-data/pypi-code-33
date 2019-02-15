# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 13:08:21 2019

@author: yili.peng
"""
from functools import wraps
import time
from glob import glob
from .cprint import cprint

def find_all_parts(factor_path):
     return glob(factor_path+'/factor_part[0-9]*')

def find_all_factors(factor_path):
    pathlist=[[i,glob(i+'/factor_[0-9]*.csv')[0]] for i in glob(factor_path+'/factor_part[0-9]*')]
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

def get_factor_part(factor_path,factor_name):
    pathlist=[[i,glob(i+'/factor_[0-9]*.csv')[0]] for i in glob(factor_path+'/factor_part[0-9]*')]
    for p in pathlist:
        line=open(p[1],'r').readline()
        if factor_name in line.strip('\n').split(',')[1:]:
            return p[0]
    print('not found')
    return None
        
def align_parms(parms):
    '''
    Making all df in parms to have the same index and column
    '''

    init=True
    set_c = {}
    set_i = {}
    for k,d in parms.items():
        if init:
            set_c = set(d.columns)
            set_i = set(d.index)
            init = False
        else:
            set_c = set_c & set(d.columns)
            set_i = set_i & set(d.index)
    list_c=list(set_c)
    list_c.sort()
    list_i=list(set_i)
    list_i.sort()
    new_parms={ k : d.reindex(index=list_i,columns=list_c) for k,d in parms.items() }
    return new_parms

def timeit(func):
    @wraps(func)
    def t(*arg,**kwarg):
        cprint('['+func.__name__+'] Started',c='',f='l')
        t0=time.time()
        r=func(*arg,**kwarg)
        t1=time.time()
        cprint('['+func.__name__ + '] Finished --- %.3f s\n'%(t1-t0),c='',f='l')
        return r
    return t