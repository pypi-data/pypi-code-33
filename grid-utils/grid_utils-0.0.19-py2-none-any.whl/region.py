# -*- coding:utf-8 -*-

import six
import numpy as np
import matplotlib.patches as mpl_patches
from matplotlib.path import Path as MPLPath
import json
from .dimension import *

try:
    from django.contrib.gis import geos
    HAS_GEODJANGO = True
except ImportError:
    HAS_GEODJANGO = False


__all__ = ['gen_region_mask']


def gen_region_mask(region, x, y):
    x, y = smart_meshgrid(x, y)
    points = np.array([x.flatten(), y.flatten()]).transpose()

    if HAS_GEODJANGO:
        path = gen_path_via_geodjango(region)
    else:
        raise RuntimeError("Requires GeoDjango")

    mask = path.contains_points(points).reshape(x.shape)
    return mask


def to_geos_multi_polygon(region):
    if not HAS_GEODJANGO:
        raise RuntimeError("Requires GeoDjango!")

    if isinstance(region, six.string_types):  # as WKT
        geometry = geos.GEOSGeometry(region)
    elif isinstance(region, dict):  # as GeoJSON
        geometry = geos.GEOSGeometry(json.dumps(region))
    else:
        geometry = region

    if isinstance(geometry, geos.Polygon):
        geometry = geos.MultiPolygon(geometry)

    if not isinstance(geometry, geos.MultiPolygon):
        raise ValueError("Cannot convert region to MultiPolygon!")

    return geometry


def gen_path_via_geodjango(region):
    mpolygon = to_geos_multi_polygon(region)
    paths = []
    for poly_arr in mpolygon.coords:
        # FIXME
        for subpoly_arr in poly_arr:
            xy = np.array(subpoly_arr)
            polygon = mpl_patches.Polygon(xy, closed=True, facecolor='none', edgecolor='none')
            paths.append(polygon.get_path())

    compound_path = MPLPath.make_compound_path(*paths)

    return compound_path



