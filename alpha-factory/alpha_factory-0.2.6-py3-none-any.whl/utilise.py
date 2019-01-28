# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 13:08:21 2019

@author: yili.peng
"""
from glob import glob

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
        
        