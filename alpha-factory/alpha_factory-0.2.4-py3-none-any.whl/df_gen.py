# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 14:59:24 2018

@author: yili.peng
"""

import pandas as pd
import numpy as np
import pkg_resources

def random_number_generator():
    return np.random.randn()*10

def formula_gen_sub(func_df,frame_df,out_name):
    notfound=True
    while notfound:
        inx=np.random.choice(func_df.index)
        notfound=False
        func_name='functions.'+func_df.loc[inx,'function_name']
        func_parm=func_df.loc[inx,'parameters']
        func_oput=func_df.loc[inx,'output']
        out_parms=[]
        out_dependency=[]
        for p in func_parm.split('|'):
            if p[:2] == 'df':
                flag=(frame_df['type'].isin(['df','cap']))
                if flag.sum()==0:
                    notfound=True
                else:
                    in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                    out_parms.append(in_df)
                    out_dependency.append(in_df)
            elif p[:2] == 'nu':
                out_parms.append(str(random_number_generator()))
            elif p[:2] == 'bo':
                if np.random.choice([True,False]):
                    out_parms.append(str(random_number_generator()))
                else:
                    flag=(frame_df['type'].isin(['df','cap']))
                    if flag.sum()==0:
                        out_parms.append(str(random_number_generator()))
                    else:
                        in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                        out_parms.append(in_df)
                        out_dependency.append(in_df)
            elif p[:2] == 'gr':
                flag=(frame_df['type']=='group')
                if flag.sum()==0:
                    notfound=True
                else:
                    in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                    out_parms.append(in_df)
                    out_dependency.append(in_df)
            elif p[:2]== 'lg':
                flag=(frame_df['type']=='lg')
                if flag.sum()==0:
                    notfound=True
                else:
                    in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                    out_parms.append(in_df)
                    out_dependency.append(in_df)
            elif p[:2]== 'ca':
                flag=(frame_df['type']=='cap')
                if flag.sum()==0:
                    notfound=True
                else:
                    in_df=np.random.choice(frame_df.loc[flag,'df_name'])
                    out_parms.append(in_df)
                    out_dependency.append(in_df)                
        if len(set(out_parms))<len(out_parms):
            notfound=True
    return pd.Series([out_name,func_name+'('+','.join(out_parms)+')','|'.join(out_dependency),func_oput],index=['df_name','equation','dependency','type'])

def formula_gen(name,frame_df_path=None,frame_df=None):
    '''
    generate one formula based on frame_df and function_frames
    
    return formula (pd.Series) and joined frame_df
    '''
    if frame_df is not None:
        pass
    elif frame_df_path is not None:
        frame_df=pd.read_csv(frame_df_path)
    else:
        raise Exception('al least one of frame_df and frame_df_path shall have values')
    func_df=pd.read_csv(pkg_resources.resource_filename('alpha_factory', 'data/functions.csv'))
    formula=formula_gen_sub(func_df=func_df,frame_df=frame_df,out_name=name)
    return formula,frame_df.append(formula,ignore_index=True)
    
    