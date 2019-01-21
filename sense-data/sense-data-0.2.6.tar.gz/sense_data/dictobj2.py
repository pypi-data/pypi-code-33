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
class stock_data():
    pass
def dict2obj(dct, obj_tag):
    for key, value in dct.items():
        if isinstance(value, dict):
            sub_obj = getattr(obj_tag, key)  # 获取真实实体字段类型
            sub_dct = dct[key]
            if ObjUtils.is_valid(sub_dct):
                dict2obj(sub_dct, sub_obj)
            else:
                setattr(obj_tag, key, None)
        elif isinstance(value, list):
            list_obj = list()
            for idx, item in enumerate(value):
                if ObjUtils.is_valid(item):
                    list_obj.append(item)
            setattr(obj_tag, key, list_obj)
        else:
            setattr(obj_tag, key, value)

    return obj_tag

