# -*- coding:utf-8 -*-

import six
import os
from .path import *


def MKDIR(dirname, rm_exist_dir=False):
    """force to make dir, no matter whether it exists"""
    #TODO: make it more robust
    if dirname in ['', '.', '..', './', '../', '/']:
        return
    orig = dirname
    if os.path.islink(orig):
        orig = find_link_orig(dirname)
    if os.path.isfile(orig):
        if not rm_exist_dir:
            raise RuntimeError('Cannot makedir: %s is file' % dirname)
    if rm_exist_dir:
        try:
            force_rm(dirname)
        except Exception as e:
            pass
    try:
        os.makedirs(dirname)
    except OSError as e:
        if e.errno != 17:
            raise e
