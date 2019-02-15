# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Functions for the numerical calculations of useful
integrals.
"""
import numpy as np
import scipy.integrate as scint

from dx_utilities.linear_algebra import project


def line_moment(path, axis_vector, order=1, n=100):
    """Evaluate numerically the moment of a path
    about a specified axis vector.

    :param path: The line geometry that represents the path.
    :type path: shapely.geometry.LineString or shapely.geometry.LinearRing
    :param tuple axis_vector: A tuple with the components of the
        reference vector about which the moment is calculated.
    :param int order: Order of the moment.
    :param n: The sampling size along the path. If ``None``, the
        points that define the path are taken into account.
    :type n: int or None
    :rtype: float
    """
    axis_vector = np.array(axis_vector)
    if n is None:
        coords = np.array(path.coords)
        cumlength = np.cumsum(np.linalg.norm(
            coords - np.append(coords[:1], coords[:-1], axis=0), axis=1
            ))
    else:
        coords = []
        cumlength = []
        for i in range(0, n+1):
            p = path.interpolate(distance=i/n, normalized=True)
            coords.append((p.x, p.y))
            cumlength.append(i*path.length/n)

        coords = np.array(coords)
        cumlength = np.array(cumlength)

    projections = project(coords, axis_vector)
    distance = np.linalg.norm(np.abs(coords - projections), axis=1)
    if order > 1:
        distance **= order

    return scint.trapz(distance, cumlength)
