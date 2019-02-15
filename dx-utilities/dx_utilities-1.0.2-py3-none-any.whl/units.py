# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Utilities to manipulate units and quantitative representations
of physical quantities.
"""
from functools import wraps

from .checks import check_numerical_value
import dx_utilities.physical_constants as CONSTANTS

from .exceptions import CodedValueError


__all__ = ['UNIT_PREFIXES', 'UnrecognizedUnitPrefix', 'Mass', 'Weight',
           'transform_value', 'inverse_transform_value', 'transform_units']


UNIT_PREFIXES = {
        'G': 1e+09,
        'M': 1e+06,
        'k': 1e+03,
        'none': 1,
        'c': 1e-02,
        'm': 1e-03,
        }


class UnrecognizedUnitPrefix(CodedValueError):
    pass


class Mass(float):
    """The mass of physical object"""

    g = CONSTANTS.g # Acceleration of gravity ``[m/s/s]``

    def to_weight(self):
        """Evaluate corresponding weight.

        :rtype: Weight
        """
        return Weight(self * self.g)

    @classmethod
    def from_weight(cls, weight):
        """Instantiate class by evaluating the mass
        of an object with given weight.

        :param float weight:
        :rtype: Mass
        """
        return cls(weight / cls.g)


class Weight(float):
    """The weight of physical object"""

    g = CONSTANTS.g # Acceleration of gravity ``[m/s/s]``

    def to_mass(self):
        """Evaluate corresponding mass.

        :rtype: Mass
        """
        return Mass(self / self.g)

    @classmethod
    def from_mass(cls, mass):
        """Instantiate class by evaluating the weight
        of an object through its mass.

        :param float mass:
        :rtype: Weight
        """
        return cls(mass * cls.g)


def transform_value(quantity, prefix='M', inverse=False):
    """Transform the value of a physical quantity expressed
    in enginnering units (e.g. ``MPa``) in the fundamental
    units of the metric system (e.g. ``kg``, ``m``, ``s``).

    :param quantity: A numerical value to transform.
    :type quantity: float or int
    :param str prefix: The unit prefix that the value is
        expressed in.
    :param bool inverse: If `True` transform a value
        expressed in fundamental units in the engineering
        form implied by the ``prefix``.
    :rtype: float or callable
    """
    if prefix not in UNIT_PREFIXES:
        raise UnrecognizedUnitPrefix(1014, f'{prefix}')

    factor = UNIT_PREFIXES[prefix]
    if inverse:
        factor = 1 / factor

    check_numerical_value(quantity)
    return factor * quantity


def inverse_transform_value(quantity, prefix='M'):
    """Wrap the ``transform_value`` function so that
    it returns the inverse transform of the quantity,
    from its representation in fundamental units, to
    a representation in engineering units.

    :param quantity: A numerical value to transform.
    :type quantity: float or int
    :param str prefix: The unit prefix that the value is
        expressed in.
    :rtype: float
    """
    return transform_value(quantity, prefix, inverse=True)


def transform_units(prefix='M', inverse=False):

    def decorator(method):

        @wraps(method)
        def transformer(*args, **kwargs):
            value = method(*args, **kwargs)
            return transform_value(value, prefix, inverse)

        return transformer

    return decorator
