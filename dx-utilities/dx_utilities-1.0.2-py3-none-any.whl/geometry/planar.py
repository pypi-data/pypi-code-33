# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Collection of abstractions representing planar geometrical shapes.

Builds on top of the shapely library
"""
from math import isclose, acos, asin, copysign, pi

import farmhash
import numpy as np
import shapely.geometry

from shapely.affinity import translate, scale, rotate
from shapely.ops import linemerge
from mathutils import Vector

from dx_utilities.checks import check_positive, check_non_negative
from dx_utilities.decorators import tolerate_input

from ..exceptions import CodedValueError, InvalidPlanarShape
from ..vectors import VectorFactory


BUFFER_RESOLUTION = 32


class PlanarShape(shapely.geometry.Polygon):
    """A class with factory methods to construct a 2-D geometric element
    with various ways.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._normal = None  # Simple cache
        self._vector = None
        self._breadth = None
        self._less = None
        self._more = None
        self._hash32 = None
        self.assert_validity()

    def assert_validity(self):
        """Assert validity of the planar-shape.

        :raises InvalidPlanarShape: If the geometry is
            invalid.
        """
        if not self.is_valid:
            raise InvalidPlanarShape(1018, ('Geometry of the planar shape '
                                            'is invalid. Try to redefine '
                                            'the shape through a boundary of '
                                            'contiguous vertices'))
    def evaluate_hash(self):
        return farmhash.hash32(';'.join(map(str, np.array(self.boundary))))

    @property
    def hash32(self):
        if self._hash32 is None:
            self._hash32 = self.evaluate_hash()
        return self._hash32

    def __hash__(self):
        return self.hash32

    @property
    def less(self):
        """Represents the region that excludes the boundary
        of this shape. Hence this property satisfies the
        following conditions:

         1. ``self.contains(self.less) is True``
         2. ``self.boundary.intersects(self.less) is False``

        :rtype: `shapely.geometry.Polygon`
        """
        if self._less is None:
            f = 1. - 1e-05
            shape = shapely.geometry.Polygon(self)
            self._less = scale(shape, *f*np.ones(3))

        return self._less

    @property
    def more(self):
        """Represents the minimum region that contains
        this shape. Constructed by scaling this shape
        up by an very small factor.

        :rtype: `shapely.geometry.Polygon`
        """
        if self._more is None:
            f = 1. + 1e-05
            shape = shapely.geometry.Polygon(self)
            self._more = scale(shape, *f*np.ones(3))

        return self._more

    @property
    def breadth(self):
        """Back-calculate the breadth of the envelope
        of the shape in the x- and y- direction.

        :rtype: tuple
        :return: ``(bx, by)``
        """
        if self._breadth is None:
            bx = self.bounds[2] - self.bounds[0]
            by = self.bounds[3] - self.bounds[1]
            self._breadth = (bx, by)
        return self._breadth

    @property
    def bx(self):
        """Breadth along x-direction."""
        return self.breadth[0]

    @property
    def by(self):
        """Breadth along y-direction."""
        return self.breadth[1]

    @classmethod
    def new(cls, shape='rectangle', *args, **kwargs):
        """Factory method that wraps all methods creating
        a specific shape.

        :param str shape: Accepts one of the following values:

            * ``rectangle`` -> `create_rectangle_by_dimensions`
            * ``box`` -> `create_rectangle_by_box`
            * ``circle`` -> `create_circle`
            * ``generic`` -> `create_generic`
            * ``angle`` -> `create_angle`

        :param \*args: Positional arguments of the wrapped methods.
        :param \*\*kwargs: Keyword arguments of the wrapped methods.
        :raises ValueError: If an unsupported shape is requested.
        :rtype: PlanarShape
        """
        if shape == 'rectangle':
            factory = cls.create_rectangle_by_dimensions
        elif shape == 'box':
            factory = cls.create_rectangle_by_box
        elif shape == 'generic':
            factory = cls.create_generic
        elif shape == 'circle':
            factory = cls.create_circle
        elif shape == 'angle':
            factory = cls.create_angle
        else:
            raise CodedValueError(1008, f"Shape {shape} cannot be created")
        return factory(*args, **kwargs)

    @classmethod
    @tolerate_input('bx', 'by', 'tx', 'ty', 'orientation')
    def create_angle(cls, bx, by, tx, ty, origin=(0., 0.), orientation=0.,
                     *args, **kwargs):
        """Create an angular section from the specified parameters.

        :param float bx: Breadth along x.
        :param float by: Breadth along y.
        :param float tx: Thickness of angle-leg along y.
        :param float ty: Thickness of angle-leg along x.
        :param tuple(float) origin: The coordinate of the point
            where the external faces of the two legs intersect.
        :param float orientation: The orientation of the angle in degrees.
            If ``0.`` the two legs extend toward the positive x- and y-axes
            respectively.
        :param \*args: For extension with positional arguments in
            subclasses.
        :param \*\*kwargs: For extension with keyword arguments in
            subclasses.
        :rtype: PlanarShape
        """
        vertices = [(0., 0.), (bx, 0.), (bx, ty), (tx, ty), (tx, by), (0., by)]
        shape = shapely.geometry.Polygon(vertices)
        shape = translate(shape, *origin)
        shape = rotate(shape, orientation, origin)
        return cls.create_generic(vertices=shape, *args, **kwargs)

    @classmethod
    def create_generic(cls, vertices=None, holes=None, *args, **kwargs):
        """Construct a planar shape by passing explicitly a sequence of vertices
        that represent its boundary, and optionaly a set of similar sequences to
        describe internal holes.

        This is a factory method that essentially wraps the superclass
        constructor.

        :param list(tuple) vertices: A list of ``(x, y)`` 2-tuples representing
            the coordinates of the shape boundary.
        :param list holes: A list of lists of ``(x, y)`` coordinate pairs, each
            representing internal holes.
        :rtype: PlanarShape
        :param \*args: For extension with positional arguments in
            subclasses.
        :param \*\*kwargs: For extension with keyword arguments in
            subclasses.
        """
        return cls(shell=vertices, holes=holes, *args, **kwargs)

    @classmethod
    def create_rectangle_by_box(cls, xymin, xymax, ccw=True, *args, **kwargs):
        """Create a rectangular box with configurable normal vector. The box
        is defined through the mininim and maximum coordinate pairs of its
        boundary.

        Wraps the `shapely.geometry.box` function.

        :param tuple(float) xymin: The minimum coordinates of the box
            ``(xmin, ymin)``.
        :param tuple(float) xymax: The maximum coordinates of the box
            ``(xmax, ymax)``.
        :param bool ccw: If true generate vertices of the polygon in the
            counter-clockwise direction.
        :rtype: PlanarShape
        :param \*args: For extension with positional arguments in
            subclasses.
        :param \*\*kwargs: For extension with keyword arguments in
            subclasses.
        """
        box = shapely.geometry.box(*xymin, *xymax, ccw)
        return cls(shell=box, *args, **kwargs)

    @classmethod
    @tolerate_input('bx', 'by')
    def create_rectangle_by_dimensions(cls, bx, by, origin=(0., 0.),
                                       position='centroid', *args, **kwargs):
        """Create a rectangular polygon by setting its dimensions and
        optionally the coordinates of a reference point. The latter may be one
        of the boundary corners or the centroid [default].

        :param float bx: Breadth of the rectangle along the local
            x-direction.
        :param float by: Breadth of the rectangle along the local
            y-direction.
        :param tuple(float) origin: The coordinates of the reference point
            of the shape.
        :param str position: The position of the reference point. Can be one of

            1. ``centroid``
            2. ``lower-left``
            3. ``lower-right``
            4. ``upper-right``
            5. ``upper-left``

        :param \*args: For extension with positional arguments in
            subclasses.
        :param \*\*kwargs: For extension with keyword arguments in
            subclasses.
        :rtype: PlanarShape
        :raises ValueError: If the dimensions passed are not positive, or
            if the value of ``pos`` is not supported.
        """
        check_positive(bx, by, emsg="Dimensions should be positive")

        box = shapely.geometry.box(-bx/2, -by/2, bx/2, by/2)
        
        reference_vector = Vector(origin)

        if position == 'centroid':
            dv = Vector((0., 0.))
        elif position == 'lower-left':
            dv = Vector((-bx/2, -by/2))
        elif position == 'lower-right':
            dv = Vector((+bx/2, -by/2))
        elif position == 'upper-right':
            dv = Vector((+bx/2, +by/2))
        elif position == 'upper-left':
            dv = Vector((-bx/2, +by/2))
        else:
            raise CodedValueError(1009, "Unsupported position on the shape")
            
        return cls(shell=translate(box, *tuple(reference_vector - dv)),
                   *args, **kwargs)

    @classmethod
    @tolerate_input('r')
    def create_circle(cls, r, center=(0., 0.), resolution=BUFFER_RESOLUTION,
                      *args, **kwargs):
        """Create a polygon that approximates a circular shape.

        :param float r: The radius of the circle.
        :param tuple center: The coordinates of the center.
        :param \*args: For extension with positional arguments in
            subclasses.
        :param \*\*kwargs: For extension with keyword arguments in
            subclasses.
        :rtype: PlanarShape
        :raises ValueError: If radius is not positive.
        """
        check_positive(r, emsg="Radius should be positive.")
        return cls(shell=shapely.geometry.Point(center).buffer(
            r, resolution=resolution
            ), *args, **kwargs)

    @classmethod
    def create_by_offset(cls, source, dx, dy=None, join_style=2, cap_style=3,
                         *args, **kwargs):
        """Create an instance of this class from the offset of
        a source geometry.
        """
        if dy is None or isclose(dx, dy):
            return cls(shell=source.buffer(
                distance=dx, join_style=join_style, cap_style=cap_style
                ), *args, **kwargs)
        offset_x = PlanarShape(shell=source.buffer(
            distance=dx, join_style=join_style, cap_style=cap_style
            ))
        offset_y = PlanarShape(shell=source.buffer(
            distance=dy, join_style=join_style, cap_style=cap_style
            ))
        if dx > dy:
            # offset_x contains offset_y
            return cls(shell=scale(offset_y, xfact=offset_x.bx/offset_y.bx),
                       *args, **kwargs)
        else:
            return cls(shell=scale(offset_x, yfact=offset_y.by/offset_x.by),
                       *args, **kwargs)

    def offset_convex_hull(self, distance, resolution=BUFFER_RESOLUTION,
                           intersect_with=None, **kwargs):
        """Construct the offset of the convex_hull of the geometry.

        :param float distance: The offset distance.
        :param int resolution: The buffer resolutioon.
        :param intersect_with: Another planar geometry that we wish
            to intersect the derived convex-hull with.
        :param \*\*kwargs: See `object.buffer` (``shapely``) for additional
            input arguments.
        :return: PlanarShape
        """
        check_non_negative(distance)
        convex_hull = self.convex_hull.buffer(
            distance, resolution=BUFFER_RESOLUTION, **kwargs
            )
        if intersect_with is not None:
            if convex_hull.boundary.intersects(intersect_with.boundary):
                convex_hull = convex_hull.intersection(intersect_with)
        return PlanarShape(shell=convex_hull)

    @property
    def normal(self):
        """A unit vector normal to the plane of the shape.

        :rtype: `mathutils.Vector`
        """
        if self._normal is None:
            self._normal = self._evaluate_normal_vector()
        return self._normal

    def _evaluate_normal_vector(self):
        """Evaluate vector normal to the plane of the shape

        :rtype: Vector
        """
        unit_vectors = VectorFactory.from_linestring(self.exterior)
        v0 = unit_vectors[0].to_3d()
        v1 = unit_vectors[1].to_3d()
        return v0.cross(v1).normalized()

    def _vectorize(self):
        """When applicable return a vector representation of the planar shape.
        That is, a vector with magnitude equal to the area of the shape and
        direction normal to the plane of the area.

        :rtype: Vector
        """
        return self.normal * self.area

    @property
    def vector(self):
        """When applicable return a vector representation of the planar shape.
        That is, a vector with magnitude equal to the area of the shape and
        direction normal to the plane of the area.

        :rtype: `mathutils.Vector`
        """
        if self._vector is None:
            self._vector = self._vectorize()
        return self._vector

    def iter_containing_envelopes(self, member):
        """Partition the envelope of this shape in four rectangles,
        each comprising the envelope of the ``member`` shape and one
        of the exterior vertices.

        :param member: A geometric shape that should be contained
            in the derived partitions. Can be any instance from
            the `shapely.geometry` package.
        :return: A generator that yields the derived partitions.
        :raises ValueError: If ``member`` shape extends beyound the bounds
            of this shape.
        """
        if not self.contains(member):
            raise CodedValueError(1010, ("Member extends beyond the bounds "
                                         "of the shape"))

        if member.geom_type == 'Polygon':
            internal_coords = member.boundary.coords[:-1]
        elif member.geom_type == 'LinearRing':
            internal_coords = member.coords[:-1]
        else:
            internal_coords = member.coords

        for vertice in self.envelope.boundary.coords[:-1]:
            coords = internal_coords + [vertice]
            yield (PlanarShape(shapely.geometry.MultiPoint(coords).envelope))

    def find_minimum_containing_envelope(self, member):
        """Among the containing envelopes of a ``member``
        return the one whose intersection with the container
        shape has the minimum area.

        :param member: A geometric shape that should be contained
            in the derived partitions. Can be any instance from
            the `shapely.geometry` package.
        :rtype: PlanarShape
        """
        return min(self.iter_containing_envelopes(member),
                   key=lambda e: e.intersection(self).area)

    def stretch_to_container(self, container, rotated=True):
        """Stretch this instance to the closest edges of
        a shape that contains it, referred to as the container.

        The following algorithm is applied:

            1. Find projections of the centroid of this
               instance to the boundary of the container.
            2. Find the two closest projections.
            3. Classify the two closest projections:

                * The projection with the larger x-coordinate
                  is the closest projection along the x-axis.
                * The projection with the larger y-coordinate
                  is the closest projection along the y-axis.

            4. Stretch the shape of this instance toward
               the two projections:

                * x-projection:

                    - Create a rectangle that extends between
                      the projection and the instance centroid
                      along x, and between the instance bounds
                      along y.

                      If the centroid does not lie within the
                      boundary of the instance, the stretch
                      rectangle extends up to the closest
                      projection of the centroid onto the instance
                      boundary along x.
                    - Rotate the rectangle so that it is perpendicular
                      to the x-projection.
                    - Join the rectangle and the shape of this
                      instance.
                    - Create the convex hull of the join.

                * y-projection: Similarly to the x-projection.

        The method returns two new shapes ``px`` and ``py``
        that correspond to the stretches toward the x- and the
        y-projection respectively.

        :param PlanarShape container:
        :param bool rotated: If `True` rotate derived shapes
            so that they align to the closest boundary edges.
        :rtype: 2-tuple
        :return: ``(px, py)``
        :raises ValueError: If the container does not contain
            the instance.
        """
        if not container.more.contains(self):
            raise CodedValueError(1011,
                                  "Container does not contain the instance")

        # Find closest projections to the container's boundary
        centroid = Vector([self.centroid.x, self.centroid.y])
        projections = container.project_to_boundary(centroid)
        dvectors = [] # centroid_to_projection vectors
        for point, ldir in projections:
            dvectors.append(Vector(point) - centroid)
        dvectors.sort(key=lambda v: v.length)

        # Filter out consecutive-parallel dvectors
        filtered_dvectors = []
        prev_tan = None
        for v in dvectors:
            this_tan = -1 if v[0] == 0. else abs(v[1]/v[0])
            if prev_tan is None or not isclose(this_tan, prev_tan):
                filtered_dvectors.append(v)
            prev_tan = this_tan
        dvectors = filtered_dvectors

        # Infer on the direction of the closest projections
        if len(dvectors) == 1:
            v = dvectors[0]
            if v[0] == 0.0:
                vy = v
                vx = Vector(([v[1], v[0]]))
            elif v[1] == 0.0:
                vx = v
                vy = Vector(([v[1], v[0]]))
            else:
                if abs(v[0]/v[1]) > abs(v[1]/v[0]):
                    vx = v
                    vy = Vector(([v[1], v[0]]))
                else:
                    vy = v
                    vx = Vector(([v[1], v[0]]))
        else:
            vx, vy = dvectors[:2]
            if vx[0] == 0.:
                vy, vx = dvectors[:2]
            elif vy[0] != 0.:
                vx = min(dvectors[:2], key=lambda v: abs(v[1]/v[0]))
                vy = max(dvectors[:2], key=lambda v: abs(v[1]/v[0]))

        proj_x = centroid + 2*vx
        proj_y = centroid + 2*vy

        if not self.more.contains(self.centroid):
            # Find closest projections of the centroid to the
            # shape's boundary.
            centroid_projections = self.project_to_boundary(centroid)
            dvectors = [Vector(point) - centroid
                        for point, _ in centroid_projections]
            dvectors.sort(key=lambda v: v.length)
            cvx = max(dvectors[:2], key=lambda v: abs(v[0]))
            cvy = max(dvectors[:2], key=lambda v: abs(v[1]))
            cproj_x = centroid + cvx
            cproj_y = centroid + cvy
        else:
            cproj_x = centroid
            cproj_y = centroid

        spx = PlanarShape.create_rectangle_by_box(
            xymin=(min(proj_x[0], cproj_x[0]), self.bounds[1]),
            xymax=(max(proj_x[0], cproj_x[0]), self.bounds[3])
            )
        spy = PlanarShape.create_rectangle_by_box(
            xymin=(self.bounds[0], min(proj_y[1], cproj_y[1])),
            xymax=(self.bounds[2], max(proj_y[1], cproj_y[1]))
            )

        if rotated:
            spx = spx.align(vx, self.centroid)
            spy = spy.align(vy, self.centroid)

        px = PlanarShape(
            shell=spx.union(self).convex_hull.intersection(container)
            )
        py = PlanarShape(
            shell=spy.union(self).convex_hull.intersection(container)
            )

        return px, py

    def distance_between_bounds(self, other):
        """Calculate the distances between the lower and upper
        bounds of this and another geometry in both directions.

        :param PlanarShape other: The target geometry.
        :return: A 4-tuple ``(dxlower, dylower, dxupper, dyupper)``
            in consistency with the representation of geometry
            bounds, i.e. ``(xlower, ylower, xupper, yupper)``
        :rtype: tuple
        """
        return tuple(
                map(abs, [s - t for (s, t) in zip(self.bounds, other.bounds)])
                )

    def project_to_boundary(self, point):
        """Project of a point lying within the
        shape onto its boundary.

        :param tuple point: The coordinates ``(x, y)``
            of the point to be projected.
        :rtype: list(tuple)
        :return: A sequence of tuples ``(point, dirv)``
            where ``point`` is the vector of each projection
            and ``dirv`` the direction of the polygon
            side on which the projection lies.
        """

        # Translate the reference coordinate system
        # to the point to be projected
        d0 = np.array(point)
        dshape = translate(self.boundary, -d0[0], -d0[1])
        # Represent the vertices
        vk = np.array(dshape)
        # Represent the direction vectors between vertices
        dvk = vk[1:] - vk[:-1]
        ndvk = dvk/np.linalg.norm(dvk, axis=1).reshape(-1, 1)
        # On the premise that
        #
        #   vp = vk + p*dvk
        #
        # where vp denotes the projection vector on the
        # new coordinate system, we are only interested
        # in vectors with p >= 0, that lie on the segment
        # v_k-v_(k+1).
        p = -np.einsum('...j,...j', vk[:-1], ndvk)
        pindex = (p >= 0) & (p <= np.linalg.norm(dvk, axis=1))
        vp = d0 + vk[:-1][pindex] + p[pindex].reshape(-1, 1)*ndvk[pindex]
        return list(zip(vp, ndvk[pindex]))

    def get_principal_direction(self, origin):
        """Given a point, evaluate its projections
        onto the boundary and find the longest
        vector from the point to its projections.

        This is defined as the principal-direction
        of the shape with reference to the given
        point.

        :param origin: The coordinates of the reference
            point.
        :type origin: `numpy.array` or `tuple` or `Point`
        :rtype: `numpy.array`
        """
        projections = self.project_to_boundary(origin)
        vectors = [v - np.array(origin) for v, _ in projections]
        major =  max(vectors, key=lambda v: np.linalg.norm(v))
        return major / np.linalg.norm(major)

    def align(self, vector, origin=None):
        """Align the shape to a vector with reference
        to a prescribed point.

        This includes the following operations:

        1. Find the principal direction of the
           shape w.r.t. the ``origin``.
        2. Evaluate the cosine and sine between
           the principal direction and the target
           vector.
        3. Rotate the shape using the trigonometric
           values of step ``(2)`` to apply an affine
           transformation about ``origin``.

        :param vector: The vector to align the shape to.
        :type vector: `tuple` or `mathutils.Vector` or `numpy.array`
        :param origin: The reference point.
        :type origin: `None` or `tuple` or `mathutils.Vector` or `numpy.array`
        :rtype: PlanarShape
        """
        if origin is None:
            origin = self.centroid
        principal_dir = self.get_principal_direction(origin)
        # Normalize vectors
        vector = vector / np.linalg.norm(vector)
        principal_dir = principal_dir / np.linalg.norm(principal_dir)
        # Evaluate trigonometric values between vectors
        c, s = np.dot(principal_dir, vector), np.cross(principal_dir, vector)
        # Perform affine rotation
        x0, y0 = np.array(origin)
        xoff = x0 - x0*c + y0*s
        yoff = y0 - x0*s - y0*c
        R = np.array([[c, -s, xoff], [s, c, yoff], [0., 0., 1.]])
        rshell = []
        for p in np.array(self.boundary):
            p = np.append(p, [1., ])
            rshell.append(R.dot(p)[:2])
        return PlanarShape(shell=rshell)

    def annotate(self, ax, text=None, anchor='lower-left', *args, **kwargs):
        xycoords = 'data'
        shape = self.envelope
        text = text or self.annotation_text
        if anchor == 'lower-left':
            delta = np.array([-self.bx/2, -self.by/2])
        elif anchor == 'lower-right':
            delta = np.array([+self.bx/2, -self.by/2])
        elif anchor == 'upper-right':
            delta = np.array([+self.bx/2, +self.by/2])
        elif anchor == 'upper-left':
            delta = np.array([-self.bx/2, +self.by/2])
        elif anchor == 'centroid':
            delta = np.array([-self.bx/2, +self.by/2])
        else:
            raise CodedValueError(1012, f'Unrecognized anchor {anchor}')
        xy = np.array(shape.centroid) + delta
        textcoords = 'offset points'
        xytext = -np.sign(delta) * np.array([10, 10])
        ax.annotate(s=text, xy=xy, xytext=xytext, xycoords=xycoords,
                    textcoords=textcoords)

    @property
    def annotation_text(self):
        return None
