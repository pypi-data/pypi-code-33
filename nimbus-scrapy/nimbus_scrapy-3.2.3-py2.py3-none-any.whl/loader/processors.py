# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import six
from datetime import datetime, date, time
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.datatypes import MergeDict
from scrapy.loader.common import wrap_loader_context


__all__ = [
    "MapComposeDefault",
    "TakeFirstDefault",
    "DTFormat",
    "TakeSecond",
]


class MapComposeDefault(object):

    def __init__(self, *functions,  **default_loader_context):
        self.default = default_loader_context.pop('default', None)
        self.functions = functions
        self.default_loader_context = default_loader_context

    def __call__(self, value, loader_context=None):
        values = arg_to_iter(value)
        if loader_context:
            context = MergeDict(loader_context, self.default_loader_context)
        else:
            context = self.default_loader_context
        wrapped_funcs = [wrap_loader_context(f, context) for f in self.functions]
        for func in wrapped_funcs:
            next_values = []
            for v in values:
                next_values += arg_to_iter(func(v))
            values = next_values
        return values or arg_to_iter(self.default)


class TakeFirstDefault(object):

    def __init__(self, default=""):
        self.default = default

    def __call__(self, values):
        if values is None:
            return self.default
        elif isinstance(values, six.string_types):
            return values
        for value in values:
            if value is not None and value != '':
                return value
        return self.default


class DTFormat(object):
    FMT_DATETIME = "%Y-%m-%d %H:%M:%S"
    FMT_DATE = "%Y-%m-%d"
    FMT_TIME = "%H:%M:%S"

    def __init__(self, format=None):
        self.format = format

    def __call__(self, value):
        if isinstance(value, (tuple, list)):
            for v in value:
                if v is not None and v != '':
                    value = v
                    break
        if isinstance(value, datetime):
            fmt = self.format or self.FMT_DATETIME
            return value.strftime(fmt)
        elif isinstance(value, date):
            fmt = self.format or self.FMT_DATE
            return value.strftime(fmt)
        elif isinstance(value, time):
            fmt = self.format or self.FMT_TIME
            return value.strftime(fmt)
        return value


class TakeSecond(object):

    def __call__(self, values):
        if len(values) >= 2:
            return values[1]



