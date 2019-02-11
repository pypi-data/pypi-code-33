# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 18:27:33 2019

@author: yili.peng
"""

import time
from functools import wraps

def cprint(text,c='b',f='h',head='',end='\n'):
    '''
    c: color  g,r,b
    f: font  h,l
    '''
    if c=='b':
        b='36;'
    elif c=='r':
        b='33;'
    elif c=='g':
        b='32;'
    else:
        b=''
    if f=='h':
        a='3;'
    elif f=='l':
        a='4;'
    else:
        a=''
    print(head+'\x1b['+a+b+'m'+str(text)+'\x1b[0m',end=end)

def wrap_text(text,leng=25):
    if len(text)>=leng:
        return text
    else:
        l=leng-len(text)
        if l%2==0:
            return ' '*(l//2)+text+' '*(l//2)
        else:
            return ' '*(l//2)+text+' '*(l//2+1)

def timeit(func):
    @wraps(func)
    def t(*arg,**kwarg):
        t0=time.time()
        r=func(*arg,**kwarg)
        t1=time.time()
        cprint(func.__name__ + ' --- %.3f s'%(t1-t0))
        return r
    return t