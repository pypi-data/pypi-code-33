# -*- coding:utf-8 -*-

import six
import cmap_utils


class ColorMap(object):
    def __init__(self, name,
                 type='Normal',
                 base_cmap_name='jet',
                 clip_min=0.0, clip_max=0.0):
        self.name = name
        self.type = type
        self.base_cmap_name = base_cmap_name
        self.base_cmap = cmap_utils.get_cmap(base_cmap_name, clip_min=clip_min, clip_max=clip_max)

    def vary(self, clip_min=0.0, clip_max=1.0, N=256):
        clip_min = float(clip_min)
        clip_max = float(clip_max)
        N = int(N)

