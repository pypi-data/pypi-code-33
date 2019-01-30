# -*- coding:utf-8 -*-

# cmap utils

import six

import numpy as np
from matplotlib import cm as mpl_cm
from matplotlib import colors as mpl_colors
from . import cm as tinkt_cm


CM_FAMILIES = {
    'mpl': mpl_cm,
    'tinkt': tinkt_cm
}


def set_under_over_bad_colors(cmap, under=None, over=None, bad=None):
    if under is not None:
        cmap.set_under(under)
    if over is not None:
        cmap.set_over(over)
    if bad is not None:
        cmap.set_bad(bad)
    return cmap


def get_cmap(base_cmap,
             clip_min=None, clip_max=None,
             N=None,
             sample_points=None,
             bad=None, over=None, under=None,
             *args, **kwargs):
    """
    Get cmap object by name, and optionally tweak it into a new one.
    Currently only supports tweaking of continuous cmaps.
    :param base_cmap: either a name or a cmap object.
    :param clip_min: lower clip point, valid range: 0.0~1.0, default: None.
    :param clip_max: upper clip point, valid range: 0.0~1.0, default: None.
    :param N: new cmap's color number, default: None (inherits from base_cmap).
    :param sample_points: a series of sampling points (0.0~1.0) on the base_cmap. When using this arg, clip_min, clip_max and N are ignored.
    :param bad: bad color, default None (inherits from base_cmap)
    :param over: over color, default None (inherits from base_cmap)
    :param under: under color, default None (inherits from base_cmap)
    :return: a cmap object (matplotlib.colors.Colormap)
    """

    if isinstance(base_cmap, tuple):
        # The tuple-form is for compatibility of old codes using metlib.color.cmap_utils.get_cmap , which read opts from json file.
        # Please neglect the complex logics and use named args whenever possible.
        return _parse_tuple_form_args_for_get_cmap(base_cmap)

    if isinstance(base_cmap, six.string_types):
        for cm_family in CM_FAMILIES.values():
            try:
                base_cmap = getattr(cm_family, base_cmap)
                break
            except AttributeError:
                pass

    if not isinstance(base_cmap, mpl_colors.Colormap):
        raise RuntimeError(u'Cannot find base_cmap: {}'.format(base_cmap))

    if sample_points is not None:
        new_name = u'Resampled from {}'.format(base_cmap.name)
        new_cmap = mpl_colors.LinearSegmentedColormap.from_list(new_name, base_cmap(sample_points))
    elif clip_min is not None or clip_max is not None:
        clip_min = 0.0 if clip_min is None else float(clip_min)
        clip_max = 0.0 if clip_max is None else float(clip_max)
        N = base_cmap.N if N is None else int(N)
        sample_points = np.linspace(clip_min, clip_max, N)
        new_name = u'Clipped from {}'.format(base_cmap.name)
        new_cmap = mpl_colors.LinearSegmentedColormap.from_list(new_name, base_cmap(sample_points))
    else:
        N = int(N) if N is not None else base_cmap.N
        new_cmap = base_cmap._resample(N)

    if bad is not None:
        new_cmap.set_bad(bad)
    elif base_cmap._rgba_bad:
        new_cmap.set_bad(base_cmap._rgba_bad)

    if over is not None:
        new_cmap.set_over(over)
    elif base_cmap._rgba_over:
        new_cmap.set_over(base_cmap._rgba_over)

    if under is not None:
        new_cmap.set_under(under)
    elif base_cmap._rgba_under:
        new_cmap.set_under(base_cmap._rgba_under)

    return new_cmap


def _parse_tuple_form_args_for_get_cmap(opts):
    # The tuple-form is for compatibility of old codes using metlib.color.cmap_utils.get_cmap, which read opts from json file.
    if len(opts) == 1:
        return get_cmap(opts[0])
    elif len(opts) == 2:
        if isinstance(opts[1], (tuple, list, np.ndarray)):
            if len(opts[1]) == 0:
                return get_cmap(opts[0])
            elif len(opts[1]) == 1:
                if isinstance(opts[1][0], (tuple, list, np.ndarray)):
                    return get_cmap(opts[0], sample_points=opts[1][0])
                else:
                    raise ValueError("")
            elif len(opts[1]) == 2:
                clip_min, clip_max = opts[1]
                N = None
            elif len(opts[1]) == 3:
                clip_min, clip_max, N = opts[1]
            else:
                return get_cmap(opts[0], sample_points=opts[1])
            return get_cmap(opts[0], clip_min=clip_min, clip_max=clip_max, N=N)
        else:
            raise ValueError("")
    else:
        raise ValueError("")
