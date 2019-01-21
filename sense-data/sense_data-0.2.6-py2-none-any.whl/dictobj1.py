#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                          
Copyright (C)2018 SenseDeal AI, Inc. All Rights Reserved                                                      
File: {name}.py
Author: xuwei                                        
Email: weix@sensedeal.ai                                 
Last modified: 2018.12.23
Description:                                            
'''
import datetime
from decimal import *

class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def dict_to_object(dictObj):
    if not isinstance(dictObj, dict):
        return dictObj
    inst = Dict()
    for k, v in dictObj.items():
        inst[k] = dict_to_object(v)
    return inst


#列表是字符串格式，通过eval变成真正的列表；列表里有多个字典，把每个字典转成对象；然后将每个对象在存入列表中，形成对象列表。
def list_to_object_list(strlist):
    try:
        if isinstance(eval(strlist), list):
            dict_list = eval(strlist)
            if len(dict_list) == 1:
                return dict_to_object(dict_list[0])
            else:
                obj_list = []
                for i in range(len(dict_list)):
                    obj_list.append(dict_to_object(dict_list[i]))
                return obj_list
        elif isinstance(eval(strlist), dict):
            return dict_to_object(eval(strlist))
    except Exception:
        return strlist