# -*- coding:utf-8 -*-

import six
import re
import numpy as np

from krux.types.check import *

__all__ = [
    'GridDim',
    'GridDimParseSerializeMixin',
    'GridDimLUTMixin',
    'GridDimBase',
]


class GridDimParseSerializeMixin(object):
    """requires: name"""
    parser = None
    serializer = None

    def parse(self, value):
        if not self.parser:
            return value

        if callable(self.parser):
            return self.parser(value)

    def serialize(self, value):
        if not self.serializer:
            return u"{}".format(value)

        if callable(self.serializer):
            return self.serializer(value)
        elif isinstance(self.serializer, six.string_types):
            if re.match(r'.*{[^{}]*}.*', self.serializer):
                return self.serializer.format(value)
            elif '%' in self.serializer:
                return self.serializer % value
            else:
                raise ValueError("Invalid serializer in dim {}: {}".format(self.name, self.serializer))


class GridDimLUTMixin(object):
    """Requires: serialize, values"""
    _true_lut = None

    @property
    def _lut(self):
        if self._true_lut is None:
            return self._build_lut(self.values)
        else:
            return self._true_lut

    def _build_lut(self, values):
        return {self.serialize(v): i for i, v in enumerate(values)}


class GridDimBase(object):
    is_grid_dim = True


class GridDim(GridDimParseSerializeMixin, GridDimLUTMixin, GridDimBase):
    _values = None

    def __init__(self, name, values, **kwargs):
        self.name = name
        self._values = values

        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)

    @property
    def ndim(self):
        if isinstance(self.name, six.string_types):
            return 1
        else:
            return len(self.name)

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

    @property
    def size(self):
        if self.ndim == 1:
            return len(self.values)
        else:
            raise NotImplementedError("Dim size for multi-dim should be implemented by user.")

    def __getitem__(self, key):
        return self.get_index(key)

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

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.name)
