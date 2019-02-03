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
import time
#from multiprocessing import Pool
#from functools import partial
warnings.simplefilter('ignore')

def generate_one(name,df,debug_mode=False,**parms):
    if debug_mode:
        from IPython import embed
    found=False
    t0=time.time()    
    while not found:
        formula,df_new=formula_gen(name=name,frame_df=df)
#        cprint(formula.equation)
        for key in formula.dependency.split('|'):
            exec(key+'=parms[\''+key+'\']')
        if debug_mode:
            try:
                exec(formula.df_name+'='+formula.equation)
            except Exception as e:
                cprint('Error {}:\t '.format(e)+formula.df_name+'='+formula.equation,c='r')
                cprint('Start a new ipython console to debug',c='r')
                embed()
                raise Exception('exec exception')
        else:
            exec(formula.df_name+'='+formula.equation)
        if is_validate(eval(formula.df_name),parms):
            found=True
#            cprint('\u2191\u2191\u2191'+wrap_text('found')+'\u2191\u2191\u2191')
    parms.update({formula.df_name:eval(formula.df_name)})
    t1=time.time()
    cprint('found {} as {} --- {:.2f} s'.format(formula.df_name,formula.equation,(t1-t0)))
    for key in parms.keys():
        exec(key+'=None')
    clean()
    return df_new,parms

def find_batch_name(df,name_start,batch_size):
    last_name=df['df_name'].iloc[-1]
    start_num=(int(''.join(list(filter(str.isdigit,last_name))))+1 if last_name.startswith(name_start) else 0)
    return [name_start+str(i) for i in range(start_num,start_num+batch_size)]

def generate_batch(df,batch_size,out_file_path,name_start,debug_mode=False,store_method='byTime',**parms):
    names=find_batch_name(df=df,name_start=name_start,batch_size=batch_size)
    parms_new=parms
    df_new=df
    d={}
    cprint(wrap_text('- - - --=[details]=-- - - -',35),c='g')
    for name in names:
        df_new,parms_new=generate_one(name=name,df=df_new,debug_mode=debug_mode,**parms_new)
        d[name]=parms_new[name]
    cprint(wrap_text('- - - --=[details]=-- - - -',35),c='g')
    if store_method == 'byTime':
        write.write_factors(path=out_file_path,file_pattern='factor',**d)
    elif store_method == 'byFactor':
        write.write_dict_to_factors(path=out_file_path,file_pattern='factor',**d)
    else:
        raise Exception('wrong value of store_method')
    names=None
    clean()
    print('process memory now: %.2f MB / %.2f MB'%(get_process_memory(),get_memory_total()))
    return df_new,parms_new,d
