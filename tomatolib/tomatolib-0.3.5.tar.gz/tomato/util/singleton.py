#!/usr/bin/python
# -*- coding:utf-8 -*-

from functools import wraps


def singleton(cls):
    _instances = {}
    @wraps(cls)
    def _singleton(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    return _singleton
