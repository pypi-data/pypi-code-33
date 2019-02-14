# -*- coding: utf-8 -*-
from math import log, exp

"""Main module."""


def powerlaw(grades=[]):
    n = len(grades)
    if n > 1:
        x = [log(i) for i in range(1, n + 1)]
        y = [log(g if g is not 0 else 0.000001) for g in grades]
        xy = [x * y for x, y in zip(x, y)]
        x2 = [x * x for x in x]
        sx = sum(x)
        sy = sum(y)
        sxy = sum(xy)
        sx2 = sum(x2)
        m = (sxy - (sx * sy / n)) / (sx2 - ((sx * sx) / n))
        b = (sy - (m * sx)) / n
        return exp((m * x[n - 1]) + b)
    elif n is 0:
        return 0
    else:
        return grades[0]
