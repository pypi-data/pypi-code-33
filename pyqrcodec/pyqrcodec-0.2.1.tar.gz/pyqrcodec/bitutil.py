#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2014年7月22日

@author: cosimzhou
'''
def copy(x):
    return x
def bit2char(x):
    return '0' if not x or x=='0' else '1'
def bool2char(x):
    return '1' if x else '0'
def char2bool(x):
    return x != '0'
def makeBits2String(x):
    if hasattr(x, '__iter__') or isinstance(x, str):
        return ''.join(map(bit2char, x))
    elif isinstance(x, int):
        return bin(x)[2:]
    else:
        return None
def makeBits2Int(x):
    if hasattr(x, '__iter__') or isinstance(x, str):
        return eval('0b'+''.join(map(bit2char, x)))#''.join(map(bit2char, gen))
    elif isinstance(x, int) or isinstance(x, long):
        return x
    else:
        return None

def strXor(str1, str2):
    assert len(str1) == len(str2)
    result = ''
    for i in xrange(len(str1)):
        result += '1' if str1[i]!=str2[i] else '0'
    return result
    
def xbin(value, bit=0):
    '''
        将数值value转为bit位的二进制字符串，不足bit位时左边补‘0’
    '''
    return bin(long(value))[2:].zfill(bit)