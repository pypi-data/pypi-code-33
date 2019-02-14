# coding=utf-8
from __future__ import print_function

import functools
import pickle

from suanpan import path

_load = functools.partial(pickle.load, fix_imports=True, encoding="latin1")
_loads = functools.partial(pickle.loads, fix_imports=True, encoding="latin1")
_dump = functools.partial(pickle.dump, fix_imports=True)
_dumps = functools.partial(pickle.dumps, fix_imports=True)


def _loadf(file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    with open(file, "w", encoding=encoding) as file:
        return _load(file, *args, **kwargs)


def _dumpf(obj, file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    path.safeMkdirsForFile(file)
    with open(file, "w", encoding=encoding) as file:
        return _dump(obj, file, *args, **kwargs)


def load(file, *args, **kwargs):
    _l = _loadf if isinstance(file, str) else _load
    return _l(file, *args, **kwargs)


def dump(obj, file, *args, **kwargs):
    _d = _dumpf if isinstance(file, str) else _dump
    return _d(obj, file, *args, **kwargs)


loads = _loads
dumps = _dumps
