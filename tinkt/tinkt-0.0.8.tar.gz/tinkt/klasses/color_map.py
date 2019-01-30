# -*- coding:utf-8 -*-

import six
import numpy as np
from krux.types.check import is_seq
from matplotlib import colors as mpl_colors
from .. import cmap_utils


class ColorMap(object):
    def __init__(self, name='unknown',
                 type='Normal',
                 base_cmap_name=None,
                 clip_min=None, clip_max=None,
                 N=None,
                 sample_points=None,
                 colors=None,
                 positions=None,
                 bad=None, over=None, under=None,
                 **kwargs
                 ):
        self.name = name
        self.type = type
        if self.type == 'Normal':
            self.base_cmap = cmap_utils.get_cmap(base_cmap_name,
                                                 clip_min=clip_min, clip_max=clip_max,
                                                 N=N,
                                                 sample_points=sample_points,
                                                 bad=bad, over=over, under=under)
        elif self.type == 'Listed':
            if colors:
                self.base_cmap = mpl_colors.ListedColormap(colors, name=self.name, N=N)
                cmap_utils.set_under_over_bad_colors(self.base_cmap, under=under, over=over, bad=bad)
            else:
                raise NotImplementedError()
        elif self.type == 'Linear':
            if colors:
                self.base_cmap = self._build_linear(name=self.name, colors=colors, positions=positions, padded=kwargs.get('padded', True), seg=kwargs.get('seg', False), N=N)
                cmap_utils.set_under_over_bad_colors(self.base_cmap, under=under, over=over, bad=bad)
            else:
                raise NotImplementedError()

    def generate(self, *args):
        if self.type in ('Normal', 'Linear'):
            return self._gen_normal(*args)
        elif self.type == 'Listed':
            return self._gen_listed(*args)

    def _gen_normal(self, clip_min=None, clip_max=None, N=None, *args, **kwargs):
        return cmap_utils.get_cmap(self.base_cmap, clip_min=clip_min, clip_max=clip_max, N=N)

    def _gen_listed(self, *args):
        # TODO: implement
        return self.base_cmap

    def _build_linear(self, name, colors, positions=None, padded=True, seg=False, N=None):
        if N is None:
            N = 256

        red = []
        green = []
        blue = []
        alpha = []
        used_pos = []
        n = len(colors)

        if positions is None:
            if seg:
                positions = np.linspace(0.0, 1.0, n+1)
            else:
                if padded:
                    positions = np.linspace(0.0, 1.0, 2*n+1)[1::2]
                else:
                    positions = np.linspace(0.0, 1.0, n)

        if seg:
            for i in range(1, n):
                pos = positions[i]
                r1, g1, b1, a1 = mpl_colors.to_rgba(colors[i-1])
                r2, g2, b2, a2 = mpl_colors.to_rgba(colors[i])
                red.append((pos, r1, r2))
                green.append((pos, g1, g2))
                blue.append((pos, b1, b2))
                alpha.append((pos, a1, a2))
                used_pos.append(pos)
        else:
            for pos, color in zip(positions, colors):
                if is_seq(color) and len(color) == 2:
                    r1, g1, b1, a1 = mpl_colors.to_rgba(color[0])
                    r2, g2, b2, a2 = mpl_colors.to_rgba(color[1])
                else:
                    r1, g1, b1, a1 = mpl_colors.to_rgba(color)
                    r2, g2, b2, a2 = r1, g1, b1, a1
                red.append((pos, r1, r2))
                green.append((pos, g1, g2))
                blue.append((pos, b1, b2))
                alpha.append((pos, a1, a2))
                used_pos.append(pos)

        if used_pos[0] > 0.001:
            first_color = colors[0]
            if is_seq(first_color) and len(first_color) == 2:
                first_color = first_color[0]
            r, g, b, a = mpl_colors.to_rgba(first_color)
            red.insert(0, (0, r, r))
            green.insert(0, (0, g, g))
            blue.insert(0, (0, b, b))
            alpha.insert(0, (0, a, a))

        if used_pos[-1] < 0.999:
            last_color = colors[-1]
            if is_seq(last_color) and len(last_color) == 2:
                last_color = last_color[1]
            r, g, b, a = mpl_colors.to_rgba(last_color)
            red.append((1, r, r))
            green.append((1, g, g))
            blue.append((1, b, b))
            alpha.append((1, a, a))

        return mpl_colors.LinearSegmentedColormap(name, {
            'red': red,
            'green': green,
            'blue': blue,
            'alpha': alpha
        }, N=N)


