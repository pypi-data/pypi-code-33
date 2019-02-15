# -*- coding:utf-8 -*-

import six
import os

__all__ = ['sorted_walk']


# status: done
def sorted_walk(top, **kwargs):
    """returns the sorted result in a list consisting os.walk's 3-tuple: (dirpath, dirnames, filename).
    kwargs: os.path's kwargs, i.e. topdown=True[, onerror=None[, followlinks=False]]"""
    kwargs.setdefault('followlinks', True)
    w = os.walk(top, **kwargs)
    res = list(w)
    res.sort()
    for stuff in res:
        stuff[1].sort()
        stuff[2].sort()
    return res

