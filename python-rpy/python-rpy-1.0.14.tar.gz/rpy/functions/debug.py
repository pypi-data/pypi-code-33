# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import time
from functools import wraps


def timed(function):
    def inner(*args, **opts):
        t = time.perf_counter()
        value = function(*args, **opts)
        return time.perf_counter() - t, value

    return inner


def echo(x):
    print(x)
    return x


def print_elapsed_time(viewfunc):
    @wraps(viewfunc)
    def inner(*args, **kw):
        t, res = timed(viewfunc)(*args, **kw)
        print("Done %s: %s sec" % (viewfunc.__name__,
                                   Decimal(time.perf_counter() - t).quantize(
                                       Decimal("0.000000"))))
        return res

    return inner
