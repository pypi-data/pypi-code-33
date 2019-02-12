# coding=utf-8

"""
Module for line class
"""

__author__ = "Morten Lind"
__copyright__ = "Morten Lind 2016"
__credits__ = ["Morten Lind"]
__license__ = "GPLv3"
__maintainer__ = "Morten Lind"
__email__ = "morten@lind.dyndns.dk"
__status__ = "Development"


import math3d as m3d
import numpy as np

from . import plane

class Line(object):
    """A line class."""

    def __init__(self, **kwargs):
        """Supported, named constructor arguments:

        * 'point_direction': An ordered pair of vectors representing a
          point on the line and the line's direction.

        * 'point', 'direction': Separate vectors for point on line and
          direction of line in named arguments.

        * 'point0', 'point1': Two points defining the line, in
        separate named arguments.
        """

        if 'point_direction' in kwargs:
            self._p, self._d = [m3d.Vector(e)
                                for e in kwargs['point_direction']]
        elif 'point' in kwargs and 'direction' in kwargs:
            self._p = m3d.Vector(kwargs['point'])
            self._d = m3d.Vector(kwargs['direction'])
        elif 'point0' in kwargs and 'point1' in kwargs:
            self._p = m3d.Vector(kwargs['point0'])
            self._d = m3d.Vector(kwargs['point1']) - self._p
        else:
            raise Exception(
                'Can not create Line object on given arguments: "{}"'
                .format(kwargs))
        # Create the unit direction vector
        self._ud = self._d.normalized

    @property
    def point(self):
        return m3d.Vector(self._p)

    @property
    def direction(self):
        return m3d.Vector(self._d)

    @property
    def unit_direction(self):
        return m3d.Vector(self._ud)


    def projected_point(self, p):
        """Return the projection of 'p' onto this line."""
        p2p = (self._p - p)
        return p + p2p - (self._ud * p2p) * self._ud

    def projected_line(self, l):
        """Return the projection of 'l' onto this line. I.e. return the point
        in this line, closest to 'l'. If the lines are parallel, the
        origin point of this line is returned.
        """
        # Check if the lines are parallel
        if (1 - self._ud * l._ud) < 10 * m3d.utils.eps:
            return self.point
        # Create the plane splanned by the common normal and the direction of the other line direction
        cn = self._ud.cross(l._ud)
        pl = plane.Plane(pn_pair=(l._p, cn.cross(l._ud)))
        # Get the intersection of this line to the plane
        return pl.line_intersection(self)


def _test():
    # Simple test of projected line.
    l1 = Line(point=(0,1,1), direction=(0,0.1,1))
    l2 = Line(point=(1,1,0), direction=(0,1,0))
    pl = l1.projected_line(l2)
    print(pl)
    assert((pl-l1.projected_point(pl)).length < 10 * m3d.utils.eps )
