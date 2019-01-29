# -*- coding:utf-8 -*-

import six
from collections import deque
from .indexed_array import *

__all__ = ['SmartIndexer']


class SmartIndexer(object):
    def __init__(self, dims):
        self.dims = dims

    @property
    def dim_names(self):
        names = []
        for dim in self.dims:
            if dim.ndim == 1:
                names.append(dim.name)
            else:
                names.extend(dim.name)
        return names

    @property
    def ndim(self):
        return sum(dim.ndim for dim in self.dims)

    @property
    def shape(self):
        sizes = []
        for dim in self.dims:
            if dim.ndim == 1:
                sizes.append(dim.size)
            else:
                sizes.extend(dim.size)
        return tuple(sizes)

    def get(self, array=None, **kwargs):
        # if array is None, return slice
        # else, return value
        raw_index = []
        for dim in self.dims:
            dim_names = [dim.name] if isinstance(dim.name, six.string_types) else dim.name
            for dim_name in dim_names:
                if dim_name in kwargs:
                    raw_index.append(kwargs[dim_name])
                else:
                    raw_index.append(slice(None))

        while len(raw_index) >= 2 and raw_index[-1] == slice(None):
            raw_index.pop()

        index = self.__getitem__(tuple(raw_index)) if raw_index else slice(None)

        if array is None:
            return index
        else:
            return array[index]

    def __getitem__(self, key):
        index = []
        if isinstance(key, tuple):
            keys = deque(key)
            for dim in self.dims:
                if len(keys) == 0:
                    break
                else:
                    dim_index = tuple(keys.popleft() for i in range(min(dim.ndim, len(keys))))
                    if len(dim_index) == 1:
                        index.append(dim[dim_index[0]])
                    else:
                        index.extend(dim[dim_index])
        return tuple(index)

    def wrap(self, array):
        return IndexedArray(array, indexer=self)

    def __repr__(self):
        return "<{} {} {}>".format(self.__class__.__name__, self.dim_names, self.shape)