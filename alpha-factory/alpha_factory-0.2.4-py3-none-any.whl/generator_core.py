# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 15:58:17 2018

@author: yili.peng
"""
from .cprint import cprint,wrap_text
from .check_mem import clean,get_process_memory,get_memory_total
from .basic_functions import functions
from .check_validation import is_validate
from .df_gen import formula_gen
from RNWS import write
import warnings
#from multiprocessing import Pool
#from functools import partial
warnings.simplefilter('ignore')


def generate_one(name,df,**parms):
#    for key in parms.keys():
#        exec(key+'=parms[\''+key+'\']')
    found=False
    while not found:
        formula,df_new=formula_gen(name=name,frame_df=df)
        cprint(formula.equation)
        for key in formula.dependency.split('|'):
            exec(key+'=parms[\''+key+'\']')
        exec(formula.df_name+'='+formula.equation)
        if is_validate(eval(formula.df_name),parms):
            found=True
            cprint('\u2191\u2191\u2191'+wrap_text('found')+'\u2191\u2191\u2191')
    parms.update({formula.df_name:eval(formula.df_name)})
    for key in parms.keys():
        exec(key+'=None')
    clean()
    return df_new,parms

#def generate_one_mul(X):
#    name,df,parms=X[0],X[1],X[2]
#    found=False
#    while not found:
#        formula,df_new=formula_gen(name=name,frame_df=df)
#        cprint(formula.equation)
#        for key in formula.dependency.split('|'):
#            exec(key+'=parms[\''+key+'\']')
#        exec(formula.df_name+'='+formula.equation)
#        if is_validate(eval(formula.df_name),parms):
#            found=True
#            cprint('\u2191\u2191\u2191 found \u2191\u2191\u2191')
#    parms.update({formula.df_name:eval(formula.df_name)})
#    for key in parms.keys():
#        exec(key+'=None')
#    clean()
#    return df_new,parms

def find_batch_name(df,name_start,batch_size):
    last_name=df['df_name'].iloc[-1]
    start_num=(int(''.join(list(filter(str.isdigit,last_name))))+1 if last_name.startswith(name_start) else 0)
    return [name_start+str(i) for i in range(start_num,start_num+batch_size)]

def generate_batch(df,batch_size,out_file_path,name_start,**parms):
    names=find_batch_name(df=df,name_start=name_start,batch_size=batch_size)
    parms_new=parms
    df_new=df
    d={}
    cprint(wrap_text('- - - --=[details]=-- - - -',35),c='g')
    for name in names:
        df_new,parms_new=generate_one(name=name,df=df_new,**parms_new)
        d[name]=parms_new[name]
    cprint(wrap_text('- - - --=[details]=-- - - -',35),c='g')
    write.write_factors(path=out_file_path,file_pattern='factor',**d)
    names=None
    clean()
    print('process memory now: %.2f MB / %.2f MB'%(get_process_memory(),get_memory_total()))
    return df_new,parms_new,d

#def generate_batch_mul(df,batch_size,out_file_path,name_start,processors=None,**parms):
#    df_new=df
#    parms_new=parms
#    names=find_batch_name(df=df,name_start=name_start,batch_size=batch_size)    
#    d={}
#    cprint('--=[multi start]=--',c='g')    
#    cprint('multiprocessing may generate duplicated factors',c='r')
#    pool=Pool(processes=processors,maxtasksperchild=1000) #frequently clear memory consumption
#    args=[(name,df,parms) for name in names]
#    results=pool.map(generate_one_mul,args)
#    pool.close()
#    pool.join()
#    cprint('--=[multi end]=--',c='g')
#    for i in range(len(names)):
#        df_tmp=results[i][0]
#        parms_tmp=results[i][1]
#        d[names[i]]=parms_tmp[names[i]]
#        df_new=df_new.append(df_tmp.iloc[-1],ignore_index=True)
#    parms_new.update(d)
#    write.write_factors(path=out_file_path,file_pattern='factor',**d)
#    df_tmp=None
#    parms_tmp=None
#    d=None
#    names=None
#    clean()
#    print('process memory now: %.2f MB / %.2f MB'%(get_process_memory(),get_memory_total()))
#    return df_new,parms_new

