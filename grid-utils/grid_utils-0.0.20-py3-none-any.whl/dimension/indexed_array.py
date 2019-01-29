# -*- coding:utf-8 -*-

__all__ = ['IndexedArray']


class IndexedArray(object):
    def __init__(self, array, indexer):
        self._array = array
        self._indexer = indexer

    def __getitem__(self, item):
        return self._array[self._indexer[item]]

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._array)

    # TODO: proxy array methods (may use netCDF4's implementation directly)

