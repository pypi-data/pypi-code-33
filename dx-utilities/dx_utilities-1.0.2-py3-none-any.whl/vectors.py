# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Vector-related utilities."""
import shapely.geometry

from math import isclose, radians
from mathutils import Vector, Matrix

from .exceptions import CodedValueError, CodedTypeError


AXIS2IDX = dict(zip(('x', 'y', 'z'), tuple(range(3))))


def rotate(vector, angle, axis='Z', degrees=False, _2D=True):
    """Rotate a `mathutils.Vector` instance about a given
    axis.

    In-place operation.

    :param vector: The vector to rotate.
    :type vector: `mathutils.Vector`
    :param float angle:
    :param str axis: ``{'X', 'Y', 'Z'}``
    :param bool radians: If `True` angle
        is assumed to be expressed in radians. Otherwise,
        it is assumed to be expressed in degrees.
    :param bool _2D: If `True` return a 2-D representation
        of the vector.
    """
    if degrees:
        angle = radians(angle)

    vector.resize_3d()
    rotation_matrix = Matrix.Rotation(angle, 3, axis)
    vector.rotate(rotation_matrix)
    if _2D:
        vector.resize_2d()


def mean(vector):
    """Reduce the vector to a scalar equal to the
    arithmetic mean of the non-zero components.

    :param vector:
    :type vector: `mathutils.Vector`
    :rtype: float
    """
    c = len([v for v in vector if not isclose(v, 0.)])
    return sum(vector)/c


class VectorFactory(Vector):
    """Factory class that provides additional methods
    to construct `mathutils.Vector` instances.
    """

    @classmethod
    def from_two_points(cls, xyz0, xyz1, normalize=False):
        """Construct a vector given two coordinates.

        :param tuple xyz0: The coordinates of the starting-point.
        :param tuple xyz1: The coordinates of the end-point.
        :param bool normalize: Set `True` to normalize the resulting
            vector.
        :rtype: Vector
        :raises ValueError: When points-coordinates are of different
            size.
        :raises ValueError: When coordinates are invalid.
        """
        if len(xyz0) != len(xyz1):
            raise CodedValueError(1015, "Points not of the same size")
        elif len(xyz0) > 3 or len(xyz0) < 2:
            raise CodedValueError(1016, "Points should have 2 to 3 coordinates")

        v = cls([xyz1[i] - xyz0[i] for i in range(len(xyz0))])
        if normalize:
            v.normalize()
        return v

    @classmethod
    def from_points(cls, points, normalize=False):
        """Generator that calculates vectors of subsequent pairs in
        a sequence of coordinate-tuples.

        :param list(tuples) points: The sequence of coordinate points.
        :param bool normalize: Set `True` to normalize resulting
            vector.
        :rtype: `mathutils.Vector`
        """
        for i0 in range(len(points)-1):
            v = cls.from_two_points(points[i0], points[i0+1], normalize)
            yield v

    @classmethod
    def from_linestring(cls, linestring, normalize=False):
        """Construct directional vectors between subsequence points
        that define a ``shapely.geometry.LineString`` or a subclass
        thereof.

        :param linestring: The linear geometry. Supported objects are
            instances of``shapely.geometry.LineString``, and of any
            subclasses thereof.
        :param bool normalize: If `True` normalize resulting vectors.
        :rtype: list(`mathutils.Vector`)
        :raises CodedTypeError: If the geometry passed is not a
            ``shapely.geometry.LineString`` instance.
        """
        if not isinstance(linestring, shapely.geometry.LineString):
            raise CodedTypeError(1017, ("Geometry passed is not a "
                                        "'shapely.geometry.LineString'"))

        return list(cls.from_points(linestring.coords, normalize))
