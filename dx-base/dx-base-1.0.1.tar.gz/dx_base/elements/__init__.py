# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Collection of abstractions representing structural elements
through a planar simplification of their geometry.
"""
import math
import numpy as np

from collections import defaultdict
from mathutils import Vector

from dx_utilities.geometry import PlanarShape
from dx_utilities.fields import (PointValue, UniformPlanarField,
                                 DiscretePlanarField)
from dx_utilities.vectors import AXIS2IDX
from dx_utilities.decorators import tolerate_input
from dx_utilities.exceptions import CodedValueError

from ..exceptions import ReinforcementError


class SteelReinforcement(object):
    """Represent amount of steel reinforcement.

    :param float As: The total area of the reinforcement.
    :param float effective_depth: The effective_depth of
        the bars on the section of interest.
    :param float spacing: The spacing between the bars.
    :param int nbars: The number of bars used.
    """

    #: Nominal bar diameters (EN 10080)
    dnominal = list(range(6, 23, 2))
    dnominal.extend([25, 28, 32, 40])
    dnominal = {dnom*1e-03 for dnom in dnominal}

    def __init__(self, As, effective_depth, spacing=1., nbars=1):
        self.d = effective_depth
        self.s = spacing
        self.total_area = As
        self.area_per_unit_breadth = self.total_area / self.s
        self.nbars = nbars
        self._phi = None

    @property
    def phi(self):
        """The diameter of the bars. If not explicitly given in
        instantiation, it is evaluated based on the total
        reinforcment area ``As`` and the number of bars ``nbars``.

        :rtype: float
        """
        if self._phi is None:
            phi = 2 * math.sqrt(self.As/self.nbars/math.pi)
            if self._phi not in self.dnominal:
                for dnom in self.dnominal:
                    if math.isclose(phi, dnom, rel_tol=1e-03):
                        self._phi = dnom
                        break
                if self._phi is None:
                    self._phi = min(filter(lambda d: d > phi, self.dnominal))
        return self._phi

    @classmethod
    def from_dimensions(cls, diameter, effective_depth, nbars=1, spacing=1.):
        """Create an instance from raw dimensions.

        :param float diameter:
        :param float effective depth:
        :param int nbars: The number of the bars
        :param float spacing: Spacing between bars
        :rtype: SteelReinforcement
        """
        unit_area = math.pi*diameter**2 / 4
        total_area = nbars * unit_area
        return cls(total_area, effective_depth, spacing, nbars=nbars)

    @property
    def As(self):
        """Alias for total reinforcement area.

        :rtype: float
        """
        return self.total_area

    @As.setter
    def As(self, value):
        self.total_area = value

    @property
    def Asbr(self):
        """Alias for area per unit breadth.

        :rtype: float
        """
        return self.area_per_unit_breadth

    @Asbr.setter
    def Asbr(self, value):
        self.area_per_unit_breadth = value

    def __add__(self, other):
        """Define addition for instances of steel-reinforcement
        as follows:

        * Areas are accumulated.
        * Effective depth and spacing are averaged by weighting
          the associated area per unit breadth.

        If ``other`` is not an instance of this class
        the addition is an identity operation.

        :rtype: SteelReinforcement
        """
        if isinstance(other, self.__class__):
            Asbr = self.Asbr + other.Asbr
            d = (self.Asbr*self.d + other.Asbr*other.d)/Asbr
            s = (self.Asbr*self.s + other.Asbr*other.s)/Asbr
            As = Asbr * s
            return self.__class__(As, d, s)
        return self

    def __radd__(self, other):
        """The reflected addition follows the
        conventions followed in the normal addition.

        :rtype: SteelReinforcement
        """
        return self + other

    def __repr__(self):
        phi = int(self.phi*1e+03)
        s = int(self.s*1e+03)
        return f"T{phi:d}@{s}"


class BaseElement(object):
    """A base-class for structural elements.

    :param material: A material object.
    :type material: BaseMaterial or None
    """

    def __init__(self, material=None, *args, **kwargs):
        self.material = material
        super().__init__(*args, **kwargs)


class PlanarElement(BaseElement, PlanarShape):
    """A base-class for 2D structural elements.

    Any instance may contain two types of objects:

    1. ``agents``: They represent dependent structural elements
       that apply some action, e.g. "columns" on a "slab".
    2. ``fields``: That represent dependent quantities distributed
       in a discrete or uniform manner in the underlying geometry.

    :param float thickness: The thickness of the element
    """
    def __init__(self, thickness=0., *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thickness = thickness
        # TODO: If linear indexing proves to be inefficient
        #       while manipulating agents and fields,
        #       construct an R-tree so that they are indexed
        #       by their geometry.
        self.agents = defaultdict(list)
        self.fields = defaultdict(list)

    @property
    def thickness(self):
        """Thickness of the element."""
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value

    def generate_agent(self, shape='rectangle', agent_type=None,
                       *args, **kwargs):
        """Create an agent instance by specifying its shape with
        reference to the coordinate system of the slab. The shape of the agent
        must lie within the geometry of the slab.

        :param str shape: The shape of the agent on the plane.
            Values supported are: ``'rectangle'``, ``'circ'`` or ``'generic'``.
        :param agent_type: The class to be used for the instantiation
            of the agent. Must be a subclass of ``PlanarShape``.
        :raises ValueError: If specified ``shape`` is not supported, or
            if the agent's geometry extends beyond the bounds of the
            slab geometry.
        :param \*args: See positional arguments in the agent-factory
            methods.
        :param \*\*kwargs: See keyword-arguments in the agent-factory
            methods.
        :return: An instance of the ``agent_type`` class.
        """
        if agent_type is None:
            agent_type = self.__class__

        agent = agent_type.new(shape=shape, *args, **kwargs)

        if self.more.contains(agent):
            return agent
        raise CodedValueError(2000, ("Specified geometry extends "
                                     "beyond the bounds of the slab"))

    def add_agent(self, label='', *args, **kwargs):
        """Add an agent instance in the respective container.

        :param str label: The label of the agent to add, e.g. "columns".
        """
        self.agents[label].append(self.generate_agent(*args, **kwargs))

    def generate_field(self, field_class, *args, **kwargs):
        """Generate a field by instantiating the specified
        ``field_class`` from `dx_utilities.fields.fields`.

        :param field_class: The class name of the field.
        :param \*args: See positional arguments in ``field_class``.
        :param \*\*kwargs: See keyword arguments in ``field_class``.
        """
        return field_class(*args, **kwargs)

    def set_field(self, label='', *args, **kwargs):
        """Add a field instance in the respective container.

        :param str label: The label of the field to add.
        :param \*args: See positional arguments in `generate_field`.
        :param \*\*kwargs: See keyword arguments in `generate_field`.
        """
        self.fields[label].append(self.generate_field(*args, **kwargs))


class RCColumn2D(PlanarElement):
    """A 2D representation of reinforced-concrete columns."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drop_panel = None

    @property
    def drop_panel(self):
        return self._drop_panel

    def set_drop_panel(self, factory=None, *args, **kwargs):
        """Set the value of the ``drop_panel`` property to
        a `ColumnDropPanel` instance (or any subclass thereof)
        generated through the `ColumnDropPanel.create_as_column_offset`
        method.

        :param factory: The class that generates the drop-panel.
        :param \*args: Positional arguments of the wrapped method.
        :param \*\*kwargs: Keyword arguments of the wrapped method.
               """
        if factory is None:
            factory = ColumnDropPanel
        self._drop_panel = factory.create_as_column_offset(
                self, *args, **kwargs
                )


class ColumnDropPanel(PlanarElement):
    """Drop-panels of slab-columns. Best to instantiate
    with `create_as_column_offset`. In that case,
    geometry is defined with reference to the parent-column.

    :param RCColumn2D column:
    :param \*args: Positional arguments in parent class.
    :param \*\*kwargs: Key-word arguments in parent class.
    """
    def __init__(self, column=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.column = column
        self._offset = None
        self._l1 = None
        self._l2 = None

    @classmethod
    @tolerate_input('lx', 'ly', 'height')
    def create_as_column_offset(cls, column, lx, height, ly=None, *args, **kwargs):
        """Generate the projection of the drop-panel as an
        offset of the parent column.

        :param RCColumn2D column: The parent structural element.
        :param float lx: The distance of the drop-panel from the
            column boundary along the x-direction.
        :param float height: The height of the drop-panel.
        :param ly: The distance of the drop-panel from the
            column boundary along the y-direction.
        :type ly: float or None
        :rtype: ColumnDropPanel
        """
        return cls.create_by_offset(column.envelope, dx=lx, dy=ly, column=column,
                                    thickness=height, *args, **kwargs)

    @property
    def height(self):
        return self.thickness

    @property
    def offset(self):
        """Offset distance from the parent column"""
        if self._offset is None:
            self._offset = self.distance_between_bounds(self.column)
        return self._offset

    @property
    def lx(self):
        return self.offset[0]

    @property
    def ly(self):
        return self.offset[1]


class RCSlab(PlanarElement):
    """2D representation of a reinforced-concrete slab.

    Reinforcement is represented as a field within the geometry
    of the slab.

    For raft slabs, or column-bases a soil-pressure field may
    be defined.

    :param str slab_type: The type of the slab. Valid options are:

        * ``'floor-slab'``: Elevated slabs.
        * ``'raft'``: Raft slabs.
        * ``'base'``: Column base.

    :raises ValueError: If an unrecognized slab-type is given.
    """

    #: slab-types that classify as 'foundation'
    foundation_types = {'raft', 'base'}
    #: All the slab-types supported by the class
    slab_types = foundation_types.union({'floor-slab'})

    def __init__(self, slab_type='floor-slab', *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not slab_type in self.slab_types:
            raise CodedValueError(2001, (f'Not valid slab-type. Choose '
                                         f'one of {self.slab_types}.'))
        self.slab_type = slab_type
        self.foundation = self.slab_type in self.foundation_types
        self._sp_index = None

    @property
    def soil_pressure(self):
        """Distribution of soil pressure under the element.
        Obviously, applies only to footings or raft foundations.

        Essentially wraps ``fields['soil-pressure']``

        :rtype: dict
        """
        return self.fields['soil-pressure']

    @property
    def rebar(self):
        """Represent the tension reinforcement though the
        distribution of the area-per-unit-breadth (As), and
        the static-height of the bars over the geometry
        of the slab.

        Essentially wraps the ``fields['rebar']`` field.

        :return: A dictionary ``{'As': list(field), 'd': list(field)}``
        :rtype: dict
        """
        return self.fields['rebar']

    # For backward compatibility
    t_rebar = rebar

    @tolerate_input('value')
    def add_soil_pressure(self, value, region=None):
        """Set uniform value of soil pressure over the specified
        region of the slab. Applies to footings and raft-foundations.
        By default the value of the soil pressure is assumed to be
        uniform throughout the entire geometry of the slab.

        :param float value:
        :param region:
        :type region: `None` or |PlanarShape|
        """
        if region is None:
            region = self
        self.set_field('soil-pressure', field_class=UniformPlanarField,
                       planarshape=region, value=value)

    def add_discrete_soil_pressure(self, coords, values, lc=None):
        """Define a `discrete planar field
        <dx_utilities.fields.fields.DiscretePlanarField>`
        of soil pressure within the geometry of the slab,
        through pairs of coordinates and values.

        The method populates ``fields['soil-pressure']``.

        :param list(tuple) coords: List of tuples ``(x, y)``.
        :param iterable values: Sequence of scalar values of soil-pressure.
        :param lc: The label of the analysis load-case, if any.
        :type lc: str or None
        """
        new_field = DiscretePlanarField.from_coords_and_values(
            coordinates=coords,
            values=np.maximum(np.zeros(len(coords)), list(values)),
            _id=lc
            )
        self.fields['soil-pressure'].append(new_field)

    @property
    def sp_index(self):
        """Index of soil-pressure field according to load-case label

        :return: A map ``{load-case: field}``.
        :rtype: dict()
        """
        if self._sp_index is None:
            self._sp_index = {f.id: f for f in self.soil_pressure}
        return self._sp_index

    def add_uniform_rebar(self, phi, s, d, nbars=1, axes='x',
                          index=None, replace=False):
        """Wrap the `add_rebar_raw` method to configure
        reinforcement on the entire slab.

        :param float phi: The diameter of the longitudinal bars.
        :param float s: Spacing of the reinforcement bars along the
            perpendicular direction.
        :param float d: Distance of the re-bars from the
            farthest compression fibre of the slab.
        :param int nbars: Number of reinforcement bars.
        :param index: The index of the reinforcement in the container.
            If `None`, a new reinforcement is indexed.
        :type index: int or None
        :param bool replace: If `True` replace reinforcement with
            the specified index. Otherwise, update by adding the new
            values. Applies only if ``index`` is not None.
        """
        self.add_rebar_raw(phi=phi, s=s, d=d, nbars=nbars, axes=axes,
                           geometry=self, index=index, replace=replace)

    def add_partial_rebar(self, phi, s, d, nbars=1, axes='x',
                          index=None, replace=False, shape='rectangle',
                          *args, **kwargs):
        """Wrap the `add_rebar_raw` method to add reinforcement
        on a limited region of the slab. This method invokes
        the |PlanarShape.new| to generate the associated geometry.

        :param float phi: The diameter of the longitudinal bars.
        :param float s: Spacing of the reinforcement bars along the
            perpendicular direction.
        :param float d: Distance of the re-bars from the
            farthest compression fibre of the slab.
        :param int nbars: Number of reinforcement bars.
        :param index: The index of the reinforcement in the container.
            If ``None``, a new reinforcement is indexed.
        :type index: int or None
        :param bool replace: If ``True`` replace reinforcement with
            the specified index. Otherwise, update by adding the new
            values. Applies only if ``index`` is not None.
        :param str shape: Shape type to generate.
        :param \*args: Positional arguments of the |PlanarShape.new|.
        :param \*\*kwargs: Positional arguments of the |PlanarShape.new|.
        :raises ValueError: If generated geometry extends beyond the
            bounds of the slab.
        """
        geometry = PlanarShape.new(shape, *args, **kwargs)
        if not self.contains(geometry.less):
            raise CodedValueError(2002, ("Generated geometry extends "
                                         "beyond the bounds of the slab"))
        self.add_rebar_raw(phi=phi, s=s, d=d, nbars=nbars, axes=axes,
                           geometry=geometry, index=index, replace=replace)

    @tolerate_input('phi', 's', 'd')
    @tolerate_input('nbars', 'index', cast=int)
    def add_rebar_raw(self, phi, s, d, nbars=1, axes='x',
                      geometry=None, index=None, replace=False):
        """Construct the representation of reinforcement bars
        from primitive parameters, i.e. diameter, spacing, and distance
        from the farthest compression fibre (effective depth).

        If no ``index`` is given, a new reinforcement representation is
        appended to the respective sequence in the container
        ``fields['rebar']``. Otherwise, the reinforcement stored at the
        specified ``index`` is updated accordingly.

        :param float phi: The diameter of the longitudinal bars.
        :param float s: Spacing of the reinforcement bars along the
            perpendicular direction.
        :param float d: Distance of the re-bars from the
            farthest compression fibre of the slab (effective_depth).
        :param int nbars: Number of reinforcement bars.
        :param str axes: The axial direction of the reinforcement bar.
            To assign the same reinforcement in more than one directions,
            concatenate the axis labels. E.g. ``'xy'`` sets the
            reinforcement in both the x- and the y-direction.
        :param geometry: The geometrical region on the slab where
            the reinforcement lies. If `None` the region coincides
            with the shape of the slab.
        :type geometry: |PlanarShape| or `None`
        :param index: The index of the reinforcement in the container.
            If `None`, a new reinforcement is indexed.
        :type index: int or None
        :param bool replace: If `True` replace reinforcement with
            the specified index. Otherwise, update by adding the new
            values. Applies only if ``index`` is not `None`.
        """
        rebar = SteelReinforcement.from_dimensions(phi, d, spacing=s,
                                                   nbars=nbars)

        vrebar = np.zeros(3, dtype=np.dtype(SteelReinforcement))
        for axis in axes:
            try:
                vrebar[AXIS2IDX[axis.lower()]] = rebar
            except KeyError:
                # Input error
                continue

        if not any(vrebar):
            raise CodedValueError(2003, "No axis specified")

        if geometry is None:
            geometry = self

        if index is None:
            self.set_field('rebar', field_class=UniformPlanarField,
                           planarshape=geometry, value=vrebar)
        else:
            rebar_field = self.fields['rebar'][index]
            if replace:
                rebar_field.replace_value(vrebar)
            else:
                rebar_field.add_value(vrebar)

    # For backward compatibility
    add_tension_rebar_raw = add_rebar_raw

    def resolve_rebar(self, geometry, contains=True):
        """Resolve the tensile reinforcement that is
        found within ``geometry``.

        :param geometry:
        :type geometry: |PlanarShape|
        :param bool contains: If `True` the method
            checks if the fields contain the ``geometry``
            specified. Otherwise, the check is limited
            to verifying intersection.
        :rtype: `list`\ (|UniformPlanarField|)
        """
        if not self.rebar:
            raise ReinforcementError(2004, ("No tensile-reinforcement "
                                            "defined on the slab"))

        containers = []
        check = 'contains' if contains else 'intersects'
        for field in self.rebar:
            if getattr(field.geometry, check)(geometry):
                containers.append(field)

        if not containers:
            raise ReinforcementError(2005, ("No tensile-reinforcement "
                                            "found in the vicinity of "
                                            "the geometry."))

        containers.sort(key=lambda f: f.geometry.intersection(geometry).area,
                        reverse=True)
        return containers
