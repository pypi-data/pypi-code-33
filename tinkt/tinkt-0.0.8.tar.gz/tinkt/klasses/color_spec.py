# -*- coding:utf-8 -*-

import six
from konfluence import Konfluence
import numpy as np
from matplotlib import colors as mpl_colors
from matplotlib import pyplot as plt

from krux.types.check import is_integer, is_seq
from tinkt.cmap_utils import get_cmap


class ColorSpec(object):
    konf = Konfluence()

    def __init__(self, name='unknown', cmap=plt.cm.jet, norm=None, vmin=None, vmax=None, levels=None, categories=None, label=None, **kwargs):
        self.name = name
        try:
            if isinstance(cmap, mpl_colors.Colormap):
                self.cmap = cmap
            elif isinstance(cmap, six.string_types):
                if cmap.startswith('colormap/'):
                    self.cmap = self.konf.get(cmap, 'default')
                else:
                    self.cmap = get_cmap(cmap)
            elif isinstance(cmap, (list, tuple, np.ndarray)):
                self.cmap = mpl_colors.ListedColormap(cmap)
            else:
                raise ValueError
        except Exception as e:
            raise ValueError(u'Cannot parse cmap: {}'.format(cmap))

        try:
            if norm is None or isinstance(norm, mpl_colors.Normalize):
                self.norm = norm
            elif isinstance(norm, six.string_types):
                self.norm = self.konf[norm]
            elif isinstance(norm, (list, tuple, np.ndarray)):
                self.norm = mpl_colors.BoundaryNorm(norm, len(norm)-1, clip=False)
            else:
                raise ValueError
        except Exception as e:
            raise ValueError(u'Cannot parse norm: {}'.format(norm))

        self._vmin = vmin
        self._vmax = vmax
        self._levels = levels
        self.categories = categories
        self.label = label

    def colorbar(self, **kwargs):
        kwargs.update({})
        clb = plt.colorbar(**kwargs)
        if self.label:
            clb.set_label(self.label)
        return clb

    @property
    def vmin(self):
        if self._vmin is not None:
            return self._vmin
        elif self.norm is not None:
            return self.norm.vmin
        else:
            return None

    @property
    def vmax(self):
        if self._vmax is not None:
            return self._vmax
        elif self.norm is not None:
            return self.norm.vmax
        else:
            return None

    @property
    def levels(self):
        if isinstance(self.norm, mpl_colors.BoundaryNorm):
            return self.norm.boundaries
        else:
            if not self._levels:
                return None

            if is_integer(self._levels):
                vmin = self.vmin
                vmax = self.vmax
                if vmin is None or vmax is None:
                    return None

                if self.norm is None:
                    return np.linspace(vmin, vmax, self._levels)
                else:
                    if isinstance(self.norm, (mpl_colors.PowerNorm, mpl_colors.LogNorm, mpl_colors.SymLogNorm)):
                        raise NotImplementedError()
                    else:
                        return np.linspace(vmin, vmax, self._levels)

            elif is_seq(self._levels):
                return self._levels
