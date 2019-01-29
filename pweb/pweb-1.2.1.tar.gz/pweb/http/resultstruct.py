#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import simplejson as json
except:
    import json

import functools
from datetime import datetime, date
from pweb.utils.datastructs import SQLRow


class JsonExtendEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        elif o.__class__.__name__ == 'SQLRow':
            return _sqlrow_dumps(o)
        else:
            return json.JSONEncoder.default(o)


def _tuple_dumps(T):
    return json.dumps(T, cls=JsonExtendEncoder)


def _list_dumps(L):
    return json.dumps(L, cls=JsonExtendEncoder)


def _dict_dumps(D):
    return json.dumps(D, cls=JsonExtendEncoder)


def _json_dumps(obj):
    return json.dumps(obj, cls=JsonExtendEncoder)


def _sqlrow_dumps(row):
    def _p(x):
        if isinstance(x, datetime):
            return x.strftime('%Y-%m-%d %H:%M:%S')
        return x

    _desc = row.cursor_description
    _vars = [_p(row._vars[x]) for x in _desc]
    return dict(zip(_desc, _vars))


def jsonresult(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        r = func(*args, **kwargs)
        # return ('text/html; charset=utf-8', _json_dumps(r))
        return ('text/html; charset=utf-8', json.dumps(r, cls=JsonExtendEncoder))

    return _wrapper


def textresult(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        r = func(*args, **kwargs)
        return ('text/plain', str(r))

    return _wrapper


if __name__ == "__main__":
    obj = dict(date=datetime.now(), k=SQLRow([]))
    print _json_dumps(obj)
