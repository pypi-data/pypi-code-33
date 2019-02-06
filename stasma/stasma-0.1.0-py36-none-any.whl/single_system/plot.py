import mpl_toolkits.mplot3d.axes3d as axes3d
import numpy as np

from astropy import units as u
from copy import copy

from stasma import utils, units, graphics

a3d = axes3d


class Plot(object):
    """
    universal plot interface for binary system class, more detailed documentation for each value of descriptor is
    available in graphics library

                        `orbit` - plots orbit in orbital plane
                        `equipotential` - plots crossections of surface Hill planes in xy,yz,zx planes
                        `mesh` - plot surface points
                        `surface` - plot stellar surfaces
    :return:
    """

    def __init__(self, instance):
        self._self = instance

    def equipotential(self, **kwargs):
        if 'axis_unit' not in kwargs:
            kwargs['axis_unit'] = u.solRad

        graphics_kwargs = ['axis_unit']

        utils.invalid_kwarg_checker(kwargs, graphics_kwargs, self._self)
        points = self._self.calculate_equipotential_boundary()
        kwargs['points'] = (points * units.DISTANCE_UNIT).to(kwargs['axis_unit'])
        graphics.equipotential_single_star(**kwargs)

    def mesh(self, **kwargs):
        if 'axis_unit' not in kwargs:
            kwargs['axis_unit'] = u.solRad

        graphics_kwargs = ['axis_unit', 'plot_axis', 'inclination', 'azimuth']
        utils.invalid_kwarg_checker(kwargs, graphics_kwargs, self._self)

        kwargs['plot_axis'] = kwargs.get('plot_axis', True)
        kwargs['inclination'] = kwargs.get('inclination', self._self.inclination)
        kwargs['mesh'] = self._self.build_mesh(return_mesh=True)
        denominator = (1 * kwargs['axis_unit'].to(units.DISTANCE_UNIT))
        kwargs['mesh'] /= denominator
        kwargs['equatorial_radius'] = self._self.star.equatorial_radius * units.DISTANCE_UNIT.to(kwargs['axis_unit'])
        kwargs['azimuth'] = kwargs.get('azimuth', 0)

        graphics.single_star_mesh(**kwargs)

    def wireframe(self, **kwargs):
        if 'axis_unit' not in kwargs:
            kwargs['axis_unit'] = u.solRad

        all_kwargs = ['axis_unit', 'plot_axis', 'inclination', 'azimuth']
        utils.invalid_kwarg_checker(kwargs, all_kwargs, self.wireframe)

        kwargs['plot_axis'] = kwargs.get('plot_axis', True)

        self._self.build_mesh()
        kwargs['mesh'], kwargs['triangles'] = self._self.build_surface(return_surface=True)
        denominator = (1 * kwargs['axis_unit'].to(units.DISTANCE_UNIT))
        kwargs['mesh'] /= denominator
        kwargs['equatorial_radius'] = self._self.star.equatorial_radius * units.DISTANCE_UNIT.to(kwargs['axis_unit'])
        kwargs['inclination'] = kwargs.get('inclination', self._self.inclination)
        kwargs['azimuth'] = kwargs.get('azimuth', 0)

        graphics.single_star_wireframe(**kwargs)

    def surface(self, **kwargs):
        if 'axis_unit' not in kwargs:
            kwargs['axis_unit'] = u.solRad

        all_kwargs = ['axis_unit', 'edges', 'normals', 'plot_axis', 'inclination', 'azimuth', 'units']
        utils.invalid_kwarg_checker(kwargs, all_kwargs, self.surface)

        kwargs['edges'] = kwargs.get('edges', True)
        kwargs['normals'] = kwargs.get('normals', False)
        kwargs['plot_axis'] = kwargs.get('plot_axis', True)
        kwargs['inclination'] = kwargs.get('inclination', self._self.inclination)
        kwargs['azimuth'] = kwargs.get('azimuth', 0)
        kwargs['units'] = kwargs.get('units', 'logg_cgs')

        self._self.build_mesh()
        output = self._self.build_surface(return_surface=True)
        kwargs['mesh'], kwargs['triangles'] = copy(output[0]), copy(output[1])
        denominator = (1 * kwargs['axis_unit'].to(units.DISTANCE_UNIT))
        kwargs['mesh'] /= denominator
        kwargs['equatorial_radius'] = self._self.star.equatorial_radius * units.DISTANCE_UNIT.to(kwargs['axis_unit'])

        kwargs['colormap'] = self._self.build_color_map()

        if kwargs['normals']:
            kwargs['arrows'] = \
                self._self.star.calculate_normals(points=kwargs['mesh'], faces=kwargs['triangles'], com=0)
            kwargs['centres'] = \
                self._self.star.calculate_surface_centres(points=kwargs['mesh'], faces=kwargs['triangles'])

        graphics.single_star_surface(**kwargs)

