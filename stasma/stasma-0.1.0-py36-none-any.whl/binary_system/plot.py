import mpl_toolkits.mplot3d.axes3d as axes3d
import numpy as np

from astropy import units as u
from stasma import utils, units, const, graphics

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

    def orbit(self, **kwargs):
        graphic_kwargs = ['start_phase', 'stop_phase', 'number_of_points', 'axis_unit', 'frame_of_reference']
        utils.invalid_kwarg_checker(kwargs, graphic_kwargs, instance_of=self._self)

        start_phase = kwargs.get('start_phase', 0.0)
        stop_phase = kwargs.get('stop_phase', 1.0)
        number_of_points = kwargs.get('number_of_points', 300)

        kwargs['axis_unit'] = kwargs.get('axis_unit', u.solRad)
        kwargs['frame_of_reference'] = kwargs.get('frame_of_reference', 'primary_component')

        if kwargs['axis_unit'] == 'dimensionless':
            kwargs['axis_unit'] = u.dimensionless_unscaled

        # orbit calculation for given phases
        phases = np.linspace(start_phase, stop_phase, number_of_points)
        ellipse = self._self.orbit.orbital_motion(phase=phases)
        # if axis are without unit a = 1
        if kwargs['axis_unit'] != u.dimensionless_unscaled:
            a = self._self.semi_major_axis * units.DISTANCE_UNIT.to(kwargs['axis_unit'])
            radius = a * ellipse[:, 0]
        else:
            radius = ellipse[:, 0]
        azimuth = ellipse[:, 1]
        x, y = utils.polar_to_cartesian(radius=radius, phi=azimuth - const.PI / 2.0)
        if kwargs['frame_of_reference'] == 'barycentric':
            kwargs['x1_data'] = - self._self.mass_ratio * x / (1 + self._self.mass_ratio)
            kwargs['y1_data'] = - self._self.mass_ratio * y / (1 + self._self.mass_ratio)
            kwargs['x2_data'] = x / (1 + self._self.mass_ratio)
            kwargs['y2_data'] = y / (1 + self._self.mass_ratio)
        elif kwargs['frame_of_reference'] == 'primary_component':
            kwargs['x_data'], kwargs['y_data'] = x, y
        graphics.orbit(**kwargs)

    def equipotential(self, **kwargs):
        graphics_kwargs = ['plane', 'phase']
        utils.invalid_kwarg_checker(kwargs, graphics_kwargs, self._self)

        kwargs['phase'] = kwargs.get('phase', 0.0)
        kwargs['plane'] = kwargs.get('plane', 'xy')

        # relative distance between components (a = 1)
        if utils.is_plane(kwargs['plane'], 'xy') or utils.is_plane(
                kwargs['plane'], 'yz') or utils.is_plane(kwargs['plane'], 'zx'):
            components_distance = self._self.orbit.orbital_motion(phase=kwargs['phase'])[0][0]
            points_primary, points_secondary = \
                self._self.compute_equipotential_boundary(components_distance=components_distance,
                                                          plane=kwargs['plane'])
        else:
            raise ValueError('invalid choice of crossection plane, use only: `xy`, `yz`, `zx`.')

        kwargs['points_primary'] = points_primary
        kwargs['points_secondary'] = points_secondary

        graphics.binary_equipotential(**kwargs)

    def mesh(self, **kwargs):
        graphics_kwargs = ['phase', 'components_to_plot', 'plot_axis', 'inclination', 'azimuth']
        utils.invalid_kwarg_checker(kwargs, graphics_kwargs, self._self)

        kwargs['phase'] = kwargs.get('phase', 0)
        kwargs['components_to_plot'] = kwargs.get('components_to_plot', 'both')
        kwargs['plot_axis'] = kwargs.get('plot_axis', True)
        kwargs['inclination'] = kwargs.get('inclination', self._self.inclination)

        components_distance, azim = self._self.orbit.orbital_motion(phase=kwargs['phase'])[0][:2]
        kwargs['azimuth'] = kwargs.get('azimuth', np.degrees(azim) - 90)

        if kwargs['components_to_plot'] in ['primary', 'both']:
            points = self._self.build_mesh(component='primary', components_distance=components_distance,
                                           return_mesh=True)
            kwargs['points_primary'] = points['primary']

        if kwargs['components_to_plot'] in ['secondary', 'both']:
            points = self._self.build_mesh(component='secondary', components_distance=components_distance,
                                           return_mesh=True)
            kwargs['points_secondary'] = points['secondary']

        graphics.binary_mesh(**kwargs)

    def wireframe(self, **kwargs):
        graphics_kwargs = ['phase', 'components_to_plot', 'plot_axis', 'inclination', 'azimuth']
        utils.invalid_kwarg_checker(kwargs, graphics_kwargs, self._self)

        kwargs['phase'] = kwargs.get('phase', 0)
        kwargs['components_to_plot'] = kwargs.get('components_to_plot', 'both')
        kwargs['plot_axis'] = kwargs.get('plot_axis', True)
        kwargs['inclination'] = kwargs.get('inclination', self._self.inclination)

        components_distance, azim = self._self.orbit.orbital_motion(phase=kwargs['phase'])[0][:2]
        kwargs['azimuth'] = kwargs.get('azimuth', np.degrees(azim) - 90)

        self._self.build_mesh(components_distance=components_distance, return_mesh=False)

        if kwargs['components_to_plot'] in ['primary', 'both']:
            points, faces = self._self.build_surface(component='primary', components_distance=components_distance,
                                                     return_surface=True)
            kwargs['points_primary'] = points['primary']
            kwargs['primary_triangles'] = faces['primary']
        if kwargs['components_to_plot'] in ['secondary', 'both']:
            points, faces = self._self.build_surface(component='secondary', components_distance=components_distance,
                                                     return_surface=True)
            kwargs['points_secondary'] = points['secondary']
            kwargs['secondary_triangles'] = faces['secondary']

        graphics.binary_wireframe(**kwargs)

    def surface(self, **kwargs):
        graphics_kwargs = ['phase', 'components_to_plot', 'normals', 'edges',
                           'plot_axis', 'inclination', 'azimuth', 'units']
        utils.invalid_kwarg_checker(kwargs, graphics_kwargs, self._self)

        kwargs['phase'] = kwargs.get('phase', 0)
        kwargs['components_to_plot'] = kwargs.get('components_to_plot', 'both')
        kwargs['normals'] = kwargs.get('normals', False)
        kwargs['edges'] = kwargs.get('edges', True)

        kwargs['plot_axis'] = kwargs.get('plot_axis', True)
        kwargs['inclination'] = kwargs.get('inclination', self._self.inclination)
        kwargs['units'] = kwargs.get('units', 'logg_cgs')

        components_distance, azim = self._self.orbit.orbital_motion(phase=kwargs['phase'])[0][:2]
        kwargs['azimuth'] = kwargs.get('azimuth', np.degrees(azim) - 90)
        kwargs['morphology'] = self._self.morphology

        self._self.build_mesh(components_distance=components_distance)
        points, faces = self._self.build_surface(components_distance=components_distance,
                                                 return_surface=True)
        kwargs['colormap'] = self._self.build_color_map(components_distance=components_distance)

        kwargs['points_primary'] = points['primary']
        kwargs['primary_triangles'] = faces['primary']
        kwargs['points_secondary'] = points['secondary']
        kwargs['secondary_triangles'] = faces['secondary']

        if kwargs['normals']:
            kwargs['primary_centres'] = self._self.primary.calculate_surface_centres(
                kwargs['points_primary'], kwargs['primary_triangles'])
            kwargs['primary_arrows'] = self._self.primary.calculate_normals(
                kwargs['points_primary'], kwargs['primary_triangles'], com=0)
            kwargs['secondary_centres'] = self._self.secondary.calculate_surface_centres(
                kwargs['points_secondary'], kwargs['secondary_triangles'])
            kwargs['secondary_arrows'] = self._self.secondary.calculate_normals(
                kwargs['points_secondary'], kwargs['secondary_triangles'], com=components_distance)

        graphics.binary_surface(**kwargs)
