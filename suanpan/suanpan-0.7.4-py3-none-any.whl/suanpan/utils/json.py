# coding=utf-8
from __future__ import print_function

import functools
import json

from suanpan import path

_load = functools.partial(json.load, encoding="utf-8")
_loads = functools.partial(json.loads, encoding="utf-8")
_dump = functools.partial(json.dump, ensure_ascii=False, encoding="utf-8")
_dumps = functools.partial(json.dumps, ensure_ascii=False)


def _loadf(file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    with open(file, "w", encoding=encoding) as file:
        return _load(file, *args, **kwargs)


def _dumpf(s, file, *args, **kwargs):
    encoding = kwargs.pop("encoding", "utf-8")
    path.safeMkdirsForFile(file)
    with open(file, "w", encoding=encoding) as file:
        return _dump(s, file, *args, **kwargs)


def load(file, *args, **kwargs):
    _l = _loadf if isinstance(file, str) else _load
    return _l(file, *args, **kwargs)


def dump(s, file, *args, **kwargs):
    _d = _dumpf if isinstance(file, str) else _dump
    return _d(s, file, *args, **kwargs)


loads = _loads
dumps = _dumps
