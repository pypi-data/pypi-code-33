# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 18:03:30 2018

@author: yili.peng
"""

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