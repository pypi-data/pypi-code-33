# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
import numpy as np
import shapely.geometry as geom

from mathutils import Vector

from ..vectors import VectorFactory


class LinearShape(geom.LineString):

    @property
    def unit_vectors(self):
        """Produce unit vectors in the direction of the boundary
        segments of the shape using `VectorFactory.from_linestring`
        method.
        """
        return VectorFactory.from_linestring(self, normalize=True)

    def truncate(self, smin, smax):
        """Truncate the shape between a minimum and maximum
        bound, expressed as fractions of the object's length.

        :param float smin: Must lie between 0. and 1.
        :param float smax: Must lie between 0. and 1.
        :rtype: `geom.LineString`
        """
        coords = np.array(self)
        filtered = [np.array(self.interpolate(smin, True))]
        for xy in coords:
            distance = self.project(geom.Point(xy), normalized=True)
            if distance > smin and distance < smax:
                filtered.append(xy)
        filtered.append(np.array(self.interpolate(smax, True)))

        return geom.LineString(filtered)

    @classmethod
    def create_arc(cls, center, radius, end_angle,
                   start_angle=0., resolution=2**8,
                   radians=True):
        """Create an arc segment.

        Following https://stackoverflow.com/a/30762727/8512915

        :param tuple center: The coordinates of the center
            of the arc.
        :param float radius:
        :param float end_angle: The end angle of the arc
            in degrees.
        :param float start_angle: The end angle of the arc
            in degrees.
        :param int resolution: The number of linear segments
            the arch is divided to.
        :param bool radians: If ``True`` the angles
            are assumed to be expressed in radians.
        :rtype: LinearShape
        """
        theta = np.linspace(start_angle, end_angle, resolution)
        if not radians:
            theta = np.radians(theta)
        x = np.around(center[0] + radius*np.cos(theta), decimals=6)
        y = np.around(center[1] + radius*np.sin(theta), decimals=6)

        return cls(np.column_stack([x, y]))

    def add_point(self, point):
        """Augment the shape by adding a point.

        :param tuple point: The coordinates of the point to
            add to the geometry.
        :rtype: LinearShape
        :return: A new linear shape augmented by the point
            specified.
        """
        new_coords = list(self.coords)
        new_coords.append(point)
        return LinearShape(new_coords)

    def merge(self, other, end_to_end=True):
        """Merge with another linear shape, even if not
        contiguous to this instance.

        :param other: The shape to merge with.
        :type other: LinearShape, LineString
        :param bool end_to_end: If ``True`` connect the
            end_point of this instance of the end-point
            of the other instance.
        :rtype: LinearShape
        """
        if end_to_end:
            new_coords = [*self.coords, *other.coords[-1::-1]]
        else:
            new_coords = [*self.coords, *other.coords]

        return LinearShape(new_coords)
