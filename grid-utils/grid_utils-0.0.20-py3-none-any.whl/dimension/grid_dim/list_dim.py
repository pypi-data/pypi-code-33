# -*- coding:utf-8 -*-

import six
from krux.types.check import *
from .grid_dim import *
from .mixins import *

__all__ = ['ListDim']


class ListDim(GridDimParseSerializeMixin, GridDimLUTMixin, GridDim):
    def __init__(self, name, values, **kwargs):
        self.name = name
        self._values = values

        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)

    @property
    def ndim(self):
        return 1

    @property
    def size(self):
        return len(self.values)

    @property
    def values(self):
        if callable(self._values):
            return self._values()
        else:
            return self._values

    @values.setter
    def values(self, new_vals):
        if callable(new_vals):
            self._values = new_vals
            self._true_lut = None
        else:
            self._values = new_vals
            self._true_lut = self._build_lut(self._values)

    def get_index(self, key, **kwargs):
        if key is None:
            return None
        elif is_integer(key):
            return key
        elif isinstance(key, slice):
            try:
                start = self.get_index(key.start, **kwargs)
            except IndexError:
                start = 0
            try:
                stop = self.get_index(key.stop, **kwargs) + 1
            except Exception:
                stop = None

            return slice(start, stop, key.step)
        else:
            try:
                return self._lut[self.serialize(key)]
            except KeyError as e:
                raise KeyError(u"{}, valid values: {}".format(key, self.values))
