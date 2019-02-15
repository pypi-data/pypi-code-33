# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Mixin-classes for field representations"""
from .base import BaseField, PointValue
from ..exceptions import CodedValueError


class UniformFieldMixin(BaseField):
    """Ensure the initialization of the uniform value
    of the field, plus a boolean indicator on whether
    the field is unbounded or not.

    :param value: The uniform value of the field.
    :type value: `float` or `mathutils.Vector`
    :param bool unbounded: If ``True`` the field is consider to be
        intrinsically unbounded.
    """
    def __init__(self, value, unbounded=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value
        self.unbounded = unbounded

    def replace_value(self, new_value):
        """
        :param new_value: The replacement uniform value of the field.
        :type new_value: `float` or `mathutils.Vector`
        """
        self.value = new_value

    def add_value(self, new_value):
        """
        :param new_value: The uniform value to add to the field.
        :type new_value: `float` or `mathutils.Vector`
        """
        self.value += new_value


class DiscreteFieldMixin(BaseField):
    """Requires the initialization of discrete `PointValue` instances
    that represent the field. The mixin provides a factory
    method that operates on raw coordinates and respective values.

    :param list(PointValue) point_values:
    """
    def __init__(self, point_values, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = point_values

    @staticmethod
    def construct_point_values(coordinates, values):
        """Construct a sequence of ``PointValue`` instances
        from a sequence of raw coordinates and a sequence of
        respective values.

        No check is implemented on whether the line connecting the
        poins is the shortest path that passes through all the points
        only once. This would require a type of sorting according
        to

        https://stackoverflow.com/questions/37742358/sorting-points-to-form-a-continuous-line

        :param list coordinates: A sequence of coordinates in the form
            ``(x, y, [z])``.
        :param list values: A sequence of values, represented by either
            scalars or vectors.
        :rtype: list
        :raises ValueError: If the number of values given does not
            match the number of points represented by the sequence
            of coordinate-tuples.
        """
        if len(coordinates) != len(values):
            raise CodedValueError(1007, ("Number of values does not match "
                                         "the number of coordinates given."))
        point_values = []
        for i, value in enumerate(values):
            point_values.append(PointValue(value, coordinates[i]))
        return point_values

    @classmethod
    def from_coords_and_values(cls, coordinates, values, *args, **kwargs):
        raise NotImplemented
