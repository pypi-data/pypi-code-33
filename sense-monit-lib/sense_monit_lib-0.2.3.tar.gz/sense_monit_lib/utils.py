#!/usr/bin/env python
# -*- coding: utf-8 -*-
def build_dic(**kwargs):
    _res = {}
    for key in kwargs:
        _res[key] = kwargs[key]
    return _res

def str2int(param):
    try:
        res = int(param)
    except:
        return None
    return res
