# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Base-classes for fields of natural quantities."""
import shapely.geometry as geom

from expiringdict import ExpiringDict
from math import isclose

from ..vectors import VectorFactory
from ..geometry import PlanarShape, LinearShape, Hash32MultiPoint
from ..exceptions import CodedValueError


__all__ = ['PointValue', 'BaseField', 'BaseLinearField', 'BasePlanarField']


class PointValue(geom.Point):
    """
    :param value: The value at the given point. May be a scalar or a vector.
        Possibly also a tensor in the future.
    :type value: `float` or `mathutils.Vector`
    :param ``*args``: See positional argument in `shapely.geometry.point.Point`
    :param ``**kwargs``: See keyword-arguments in `shapely.geometry.point.Point`.
    """
    def __init__(self, value, *args, **kwargs):
        super(PointValue, self).__init__(*args, **kwargs)
        # TODO: Make proper checks of the value type
        self.value = value

    @classmethod
    def create_point_vector(cls, coords, vector_value):
        """Create an instance by passing coordinates and the vector
        components.

        :param tuple coords: Coordinates ``(x, y, [z])`` of the point.
        :param tuple vector_value: Components ``(vx, vy, [vz])`` of the
            vector.
        :rtype: PointValue
        """
        return cls(VectorFactory(vector_value), coords)


class BaseField(object):
    """A base-class to represent the field of a physical quantity.

    A field is assigned to a characteristic geometry. This can either
    represent the external bounds of the field, or a directional vector
    for unbounded distributions of a physical quantity.

    :param geometry: The shape of the external boundary of the field.
    """

    def __init__(self, geometry, _id=None):
        self.geometry = geometry
        self.id = _id


class BaseLinearField(BaseField):
    """Base class for uni-directional linear fields. Requires a linear
    geometry representing the direction, or a bounded section, where
    the field is present.

    :param LinearShape line: The linear geometry of the field.
    """
    def __init__(self, line, *args, **kwargs):
        super(BaseLinearField, self).__init__(geometry=line, *args, **kwargs)
        self.direction = self.evaluate_direction()

    def evaluate_direction(self):
        """Evaluate the unit vector that complies with the linear geometry
        given.

        :rtype: `mathutils.Vector`
        :raises ValueError: If ``line`` has segments that are not collinear.
        """
        vectors = self.geometry.unit_vectors
        v0 = vectors.pop()
        dot_product = 1.
        while vectors:
            v1 = vectors.pop()
            dot_product *= v0.dot(v1)
            if not isclose(dot_product, 1., rel_tol=1e-04):
                raise CodedValueError(1006, "Not all segments in linestring are collinear.")
            v0 = v1

        return v0


class BasePlanarField(BaseField):
    """The base class for a planar field. Requires that it is assigned to
    a `PlanarShape`.

    :param PlanarShape planarshape: The geometry of the planar field.
    """

    def __init__(self, planarshape, *args, **kwargs):
        super().__init__(geometry=planarshape, *args, **kwargs)
        self.normal = self.geometry.normal


class FieldPointsCache(ExpiringDict):

    def get(self, coordinates, *args, **kwargs):
        key = FieldPoints.evaluate_hash(coordinates)
        return super().get(key, *args, **kwargs)


class FieldPoints(Hash32MultiPoint):
    """A cacheable collection of field-points.

    :param iterable coordinates: A sequence of coordinate tuples
        representing the points.
    :param \*args:
    :param \*\*kwargs:
    """
    cache_len = 128
    cache_age_secs = 360
    cache = FieldPointsCache(max_len=cache_len, max_age_seconds=cache_age_secs)

    def __init__(self, coordinates, *args, **kwargs):
        super().__init__(coordinates, *args, **kwargs)
        self.cache[self.hash32] = self
