# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 14:26:43 2018

@author: yili.peng
"""

import pandas as pd

def write_line_rec(df,sub_name):
    sub_chosen_srs=df.loc[sub_name]
    if pd.isnull(sub_chosen_srs.dependency):
        return ['input->'+sub_chosen_srs.equation]
    else:
        line=[]
        for subsub_name in sub_chosen_srs.dependency.split('|'):
            line.extend(write_line_rec(df,subsub_name))
        line.extend([sub_name+' = '+sub_chosen_srs.equation])
        return line 

def clean_line(line):
    new_line=[]
    start=[]
    for i in line:
        if (i[:7]=='input->'):
            if (i[7:] not in start):
                start.append(i[7:])
        elif i in new_line:
            pass
        else:
            new_line.append(i)
    return start,new_line

def output_name(name,df):
    line_raw=write_line_rec(df=df,sub_name=name)
    start,line=clean_line(line_raw)
    line.append('return '+name)
    one_factor='\nclass '+name+':\n   def generator('+','.join(start)+',**kwarg):\n      '+'\n      '.join(line)
    return one_factor

def write_core(df):
    lines=''
    for name in df.index[~pd.isnull(df.dependency)]:
        one_factor=output_name(name,df)
        lines+=one_factor+'\n'
    return lines

def write_start():
    start_lines=['# -*- coding: utf-8 -*-','\n','from alpha_factory.basic_functions import functions','\n']
    return ''.join(start_lines)

def write_file(df,path):
    with open(path,'w',encoding='utf-8') as f:
        f.write(write_start())
        f.write(write_core(df))