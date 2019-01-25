#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      leveldb.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    tangmi(tangmi360@gmail.com)
    @date:      September 04, 2018
    @desc:      LevelDB
"""

import os
import leveldb

class LevelDB(object):
    def __init__(self, *args, **kwargs):
        exists_dir = os.path.exists(args[0])
        if not exists_dir:
            os.makedirs(args[0])
        self._leveldb = leveldb.LevelDB(*args, **kwargs)

    def __getattr__(self, attr):
        return getattr(self._leveldb, attr)
