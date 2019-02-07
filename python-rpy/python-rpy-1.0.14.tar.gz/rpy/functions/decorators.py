# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from rpy.functions.datastructures import data
from rpy.functions.functional import composition


def decorate(*func):
    def inner(fn):
        return composition(fn, *func)
    return inner


to_tuple = decorate(tuple)
to_dict = decorate(dict)
to_data = decorate(data)
