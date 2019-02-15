# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Operations on geometric shapes."""
import numpy as np

import shapely.geometry as geom
from shapely.ops import linemerge

from dx_utilities.linear_algebra import reflect as coord_reflect


def reflect(shape, normal=(1., 0.), delete_original=False,
            origin=(0., 0.)):
    """Reflect a shape with respect to a plane with
    the specified normal.

    :param shape: The shape to be reflected.
    :type shape: `shapely.geometry.LineString` or
        `shapely.geometry.LinearRing` or
        `shapely.geometry.MultiLineString` or `LinearShape`
    :param tuple normal: The normal to the projection
        plane.
    :param bool delete_original: If `True` return
        a representation of the reflection only. Otherwise
        return the original as well.
    :param tuple origin: The coordinates of the origin
        of the projection plane.
    :rtype: `shapely.geometry.LineString` or `shapely.geometry.MultiLineString`
    """
    try:
        to_reflect = [*shape.geoms]
    except AttributeError:
        coords = np.around(shape.coords, decimals=6)
        to_reflect = [geom.LineString(coords)]

    rcoords = []
    for g in to_reflect:
        coords = np.around(np.array(g.coords), decimals=6)
        rcoords.append(coord_reflect(coords, normal, origin))
    reflections = map(geom.LineString, rcoords)
    if delete_original:
        return linemerge([*reflections])
    return linemerge([*to_reflect, *reflections])
