# -*- coding:utf-8 -*-

import six
from .grid_dim import *
from .mixins import *
from grid_utils.gridder import XYProjGridder
from krux.types.check import is_integer, is_float

__all__ = ['XYDim']


class XYDim(GridDimParseSerializeMixin, GridDim, XYProjGridder):
    def __init__(self, name=('y', 'x'), x=None, y=None, proj=None, nx=None, ny=None, dx=None, dy=None, x_orig=None, y_orig=None, **kwargs):
        assert len(name) == 2
        self.name = name

        super(XYDim, self).__init__(proj=proj, x=x, y=y,
                                    nx=nx, ny=ny,
                                    dx=dx, dy=dy,
                                    x_orig=x_orig, y_orig=y_orig,
                                    **kwargs)

        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)

    @property
    def ndim(self):
        return 2

    @property
    def size(self):
        return self.ny, self.nx

    @property
    def values(self):
        return self.X, self.Y

    @values.setter
    def values(self, new_vals):
        x, y = new_vals
        self.set_xy(x, y)

    def get_index(self, key, **kwargs):
        if is_integer(key):
            return key
        elif isinstance(key, slice):
            if self._is_normal_index_or_slice(key):
                return key
            else:
                y1, j1_fixed = (None, True) if is_integer(key.start) else (key.start, False)
                y2, j2_fixed = (None, True) if is_integer(key.stop) else (key.stop, False)

                i1, j1, i2, j2 = self.get_bounding_ij(x1=None, y1=y1, x2=None, y2=y2)

                j1 = key.start if j1_fixed else j1
                j2 = key.stop if j2_fixed else j2

                return slice(i1, i2, key.step)
        elif isinstance(key, tuple):
            if len(key) != 2:
                raise KeyError(key)

            y_normal = self._is_normal_index_or_slice(key[0])
            x_normal = self._is_normal_index_or_slice(key[1])
            if y_normal and x_normal:
                return key
            elif is_float(key[0]) and is_float(key[1]):
                i, j = self.x2i(key[1], key[0])
                return j, i
            elif isinstance(key[0], slice) and isinstance(key[1], slice):
                y1, j1_fixed = (None, True) if is_integer(key[0].start) else (key[0].start, False)
                y2, j2_fixed = (None, True) if is_integer(key[0].stop) else (key[0].stop, False)
                x1, i1_fixed = (None, True) if is_integer(key[1].start) else (key[1].start, False)
                x2, i2_fixed = (None, True) if is_integer(key[1].stop) else (key[1].stop, False)

                i1, j1, i2, j2 = self.get_bounding_ij(x1, y1, x2, y2)
                i1 = key[1].start if i1_fixed else i1
                i2 = key[1].start if i2_fixed else i2
                j1 = key[0].start if j1_fixed else j1
                j2 = key[0].start if j2_fixed else j2
                return slice(j1, j2, key[0].step), slice(i1, i2, key[1].step)
            else:
                raise NotImplementedError(u"Index type ({}, {}) not supported yet".format(type(key[0]), type(key[1])))

    def _is_normal_index_or_slice(self, i):
        if is_integer(i):
            return True
        if isinstance(i, slice):
            return (i.start is None or is_integer(i.start)) and (i.stop is None or is_integer(i.stop))

        return False
