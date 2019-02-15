# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Collection of abstractions to represent fields of physical quantities
of interest.
"""
import shapely.geometry as geom

from .base import BaseLinearField, BasePlanarField, FieldPoints
from .mixins import UniformFieldMixin, DiscreteFieldMixin
from ..vectors import VectorFactory
from ..geometry import PlanarShape, LinearShape


__all__ = ['BaseLinearField', 'UniformLineField', 'DiscreteLineField',
           'UniformPlanarField', 'DiscretePlanarField']


class UniformLineField(BaseLinearField, UniformFieldMixin):
    """Specifies a uniform unidirectional field acting on a
    linear segment or an unbounded line.

    :param LinearShape line: The geometry of the field.
    :param value: Uniform Value of the field.
    :type value: `float` or `mathutils.Vector`
    :param bool unbounded: Specifies whether the field is
        unbounded or not.
    """
    pass


class DiscreteLineField(BaseLinearField, DiscreteFieldMixin):
    """Specifies a discrete line field. The class is designed
    to be constructed from the factory-method `from_coords_and_values`.

    :param LinearShape line:
    :param list(PointValue) point_values:
    """

    def __init__(self, line, point_values):
        super().__init__(line=line, point_values=point_values)
        self.values = point_values

    @classmethod
    def from_coords_and_values(cls, coordinates, values):
        """Create an instance from a sequence of raw coordinates, and
        a sequence of respective values.

        No check is implemented on whether the line connecting the
        poins is the shortest path that passes through all the points
        only once. This would require some sort of sorting according
        to

        https://stackoverflow.com/questions/37742358/sorting-points-to-form-a-continuous-line

        :param list coordinates: A sequence of coordinates in the form
            ``(x, y, [z])``.
        :param list values: A sequence of values, represented by either
            scalars or vectors.
        :rtype: DiscreteLineField
        """
        point_values = cls.construct_point_values(coordinates, values)
        line = LinearShape(coordinates)
        return cls(line, point_values)


class UniformPlanarField(BasePlanarField, UniformFieldMixin):
    """A planar field with uniform value within its bounds.

    :param PlanarShape planarshape: The geometry of the planar field.
    :param value: The value of the uniform field.
    :type value: `float` or `mathutils.Vector`
    :param bool unbounded:
    """
    pass


class DiscretePlanarField(BasePlanarField, DiscreteFieldMixin):
    """A planar field with discrete point-values within its bounds.

    :param PlanarShape planarshape: The geometry of the planar field.
    :param list(PointValue) point_values:
    """

    def __init__(self, points=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = None
        self.points = points

    @property
    def index(self):
        if self._index is None:
            self._index = {(pv.x, pv.y): pv.value for pv in self.values}
        return self._index

    @classmethod
    def from_coords_and_values(cls, coordinates, values, geometry=None, **kwargs):
        """Create an instance from a sequence of raw coordinates, and
        a sequence of respective values.

        The set of coordinates, however, does not uniquely imply the
        planar geometry of the field. It only represents a sample
        of the field-values within the actual geometry. The latter
        may well assume the envelope of the set of coordinates at its
        external boundary, or their convex hull, or any other polygon
        that contains the points given.

        Hence, if no explicit geometry is given trough the input
        arguments, it is assumed that the actual planar geometry of
        the field is bounded by the envelope of the points given.


        :param list coordinates: A sequence of coordinates in the form
            ``(x, y, [z])``.
        :param list values: A sequence of values, represented by either
            scalars or vectors.
        :param geometry: The planar geometry that bounds the discrete
            field.
        :rtype: DiscretePlanarField
        :raises ValueError: If the number of values given does not
            match the number of points represented by the sequence
            of coordinate-tuples.
        """
        point_values = cls.construct_point_values(coordinates, values)
        points = FieldPoints.cache.get(coordinates)
        points = points or FieldPoints(coordinates)
        if geometry is None:
            geometry = PlanarShape(points.convex_hull)
        return cls(point_values=point_values, planarshape=geometry,
                   points=points, **kwargs)

    def query_avg(self, geometry):
        """Query this field with a geometry in order
        to evaluate the average value of the field
        in their intersection.

        :param geometry: The geometric configuration
            of a shape in which we want to evaluate
            the average value of the field.
        :type geometry: Any `shapely` geometry
            that supports the intersection operation.
        """
        values = []
        points = self.points.intersection(geometry)
        try:
            for p in self.points.intersection(geometry):
                values.append(self.index[(p.x, p.y)])
        except TypeError:
            values.append(self.index[(points.x, points.y)])
        if values:
            return sum(values) / len(values)
        return 0.
