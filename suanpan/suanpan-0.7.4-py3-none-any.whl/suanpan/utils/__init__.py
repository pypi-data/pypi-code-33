# coding=utf-8
from __future__ import print_function

import collections
import functools


def merge(*dicts):
    def _merge(result, item):
        result.update(item)
        return result

    return functools.reduce(_merge, dicts, {})


def count(iterable):
    if hasattr(iterable, "__len__"):
        return len(iterable)

    d = collections.deque(enumerate(iterable, 1), maxlen=1)
    return d[0][0] if d else 0
