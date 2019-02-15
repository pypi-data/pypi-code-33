# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
from shapely.geometry import MultiPoint

import functools
import farmhash


class Hash32MultiPoint(MultiPoint):
    """Hashable variation of the ``MultiPoint`` class.

    A 32-bit hash is evaluated from a concatenated
    string representation of the coordinates of the
    points.
    """

    def __init__(self, coordinates, *args, **kwargs):
        super().__init__(coordinates, *args, **kwargs)
        self.coordinates = coordinates
        self._hash32 = None

    @functools.lru_cache(maxsize=128)
    def intersection(self, other, *args, **kwargs):
        """Cachable variation of the intersection operation
        of the super class.

        :param other: The geometry to intersect with this
            instance.
        :type other: Any ``shapely`` geometric object that
            supports the operation.
        :param \*args:
        :param \*\*kwargs:
        """
        return super().intersection(other, *args, **kwargs)

    @staticmethod
    def stringify(coordinates):
        return ';'.join(map(str, coordinates))

    def __str__(self):
        return self.stringify(self.coordinates)

    @staticmethod
    def evaluate_hash(coordinates):
        return farmhash.hash32(Hash32MultiPoint.stringify(coordinates))

    @property
    def hash32(self):
        if self._hash32 is None:
            self._hash32 = farmhash.hash32(str(self))
        return self._hash32

    def __hash__(self):
        return self.hash32
