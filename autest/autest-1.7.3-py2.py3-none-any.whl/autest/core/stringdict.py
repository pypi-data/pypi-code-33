from __future__ import absolute_import, division, print_function
from itertools import chain
import autest.common.is_a as is_a
import hosts.output as host
from .debug import get_user_frame

class StringDict(dict):
    def __init__(self, mapping=(), **kwargs):
        # dicts take a mapping or iterable as their optional first argument
        super(StringDict, self).__init__(self._process_args(mapping, **kwargs))

    @staticmethod
    def _process_args(mapping=(), **kwargs):
        if hasattr(mapping, 'items'):
            mapping = getattr(mapping, 'items')()
        ret = []
        for k, v in chain(mapping, getattr(kwargs, 'items')()):
            if not is_a.String(v):
                host.WriteError(
                    "Value must be a string",
                    stack=get_user_frame(2)
                )
            ret.append((k, v))
        return ret

    def __setitem__(self, k, v):
        if not is_a.String(v):
            host.WriteError(
                "Value must be a string",
                stack=get_user_frame(1)
            )
        return super(StringDict, self).__setitem__(k, v)

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, super(StringDict, self).__repr__())

    def update(self, mapping=(), **kwargs):
        super(StringDict, self).update(self._process_args(mapping, **kwargs))

