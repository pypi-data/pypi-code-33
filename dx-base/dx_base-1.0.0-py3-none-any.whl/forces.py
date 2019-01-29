# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Collection of abstractions representing forces
and stresses.
"""
from ctypes import c_double

import numpy as np

from dx_utilities.array_interface import typestr


class NodalForces(object):
    """Set of forces and moments on a node, with 6
    degrees-of-freedom in the most general case.

    All values refer to a local-coordinate system to
    be defined on top.

    :param str LC: Name of the load-case or combination.
    :param float Rx: Force in the x direction
    :param float Ry: Force in the y direction
    :param float Rz: Force in the z direction
    :param float Mx: Moment in the x direction
    :param float My: Moment in the y direction
    :param float Mz: Moment in the z direction
    """

    #: Degrees of freedom
    dof = 6

    def __init__(self, LC="LC0", Rx=0., Ry=0., Rz=0., Mx=0., My=0., Mz=0.):
        self.LC = LC
        self.Rx = Rx
        self.Ry = Ry
        self.Rz = Rz
        self.Mx = Mx
        self.My = My
        self.Mz = Mz

    @property
    def container(self):
        """List of nodal forces ``[Rx, Ry, Rz, Mx, My, Mz]``

        :rtype: list
        """
        return [self.Rx, self.Ry, self.Rz, self.Mx, self.My, self.Mz]

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i == self.dof:
            raise StopIteration
        value = self.container[self.i]
        self.i += 1
        return value

    @property
    def typestr(self):
        """A string providing the basic type of the homogeneous array.
        For more details see the docs on `array interface`_.

        :rtype: str
        """
        return typestr()

    @property
    def ctypes(self):
        """c-type representation of the container.

        :rtype: array of c-double
        """
        array_type = c_double * self.dof
        data = array_type()

        i = 0
        for v in self:
            data[i] = v
            i += 1

        return data

    def array_interface(self):
        """Construct the `numpy` `array interface`_ for class instances.
        The array interface enables the vectorization of the class
        through `numpy.array`.

        :rtype: dict
        """
        ai = {'shape': (1, self.dof), 'typestr': self.typestr, 'version': 3}
        ai['data'] = self.ctypes
        return ai

    __array_interface__ = property(array_interface)

    def __add__(self, other):
        new_container = np.array(self.container) + np.array(other.container)
        return self.__class__(self.LC, *new_container)


class NMyMz(NodalForces):

    dof = 3

    def __init__(self, LC='LC0', N=0., My=0., Mz=0., **kwargs):
        super().__init__(LC=LC, Rx=N, My=My, Mz=Mz, **kwargs)
        self.N = self.Rx

    @property
    def container(self):
        return [self.N, self.My, self.Mz]
