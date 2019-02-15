# -*- coding:utf-8 -*-

import os
from ..path import *
from .rm import RM

__all__ = ['MKDIR']


def MKDIR(dir_path, force=False):
    #TODO: make it more robust
    if dir_path in ['', '.', '..', './', '../', '/']:
        return
    orig = dir_path
    if is_link(orig):
        orig = find_link_orig(dir_path)
    if is_file(orig):
        if not force:
            raise RuntimeError('Cannot makedir: %s is file' % dir_path)
    if force:
        try:
            RM(dir_path)
        except Exception as e:
            pass
    try:
        os.makedirs(dir_path)
    except OSError as e:
        if e.errno != 17:
            raise e

