from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from mpl_toolkits.mplot3d import axes3d

from stasma import utils


def orbit(**kwargs):
    """
    Plot function for descriptor = `orbit` in function BinarySystem.plot(). This function plots orbit of the secondary
    component in the reference frame of the primary component.

    :param kwargs:
            :**kwargs options**:
                * **axis_unit** * --  e.g. astropy.units.solRad;
                    unit in which axis will be displayed, please use
                                                               astropy.units format, default unit is solar radius
                                                               if you want dimensionless axis, use
                                                               astropy.units.dimensionless_unscaled or `dimensionless`
                * **frame_or_reference** * --  str;
                    origin point for frame of reference in which orbit will be displayed, choices:
                                                                       `primary_component`
                                                                       `barycentric`
    :return:
    """
    unit = kwargs['axis_unit']
    frame_of_reference = kwargs['frame_of_reference']

    if unit == u.dimensionless_unscaled:
        x_label, y_label = 'x', 'y'
    else:
        x_label, y_label = r'x/' + str(unit), r'y/' + str(unit)

    f = plt.figure()
    ax = f.add_subplot(111)
    ax.grid()
    if frame_of_reference == 'barycentric':
        x1, y1 = kwargs['x1_data'], kwargs['y1_data']
        x2, y2 = kwargs['x2_data'], kwargs['y2_data']
        ax.plot(x1, y1, label='primary')
        ax.plot(x2, y2, label='secondary')
        ax.scatter([0], [0], c='black', s=4)
    elif frame_of_reference == 'primary_component':
        x, y = kwargs['x_data'], kwargs['y_data']
        ax.plot(x, y, label='secondary')
        ax.scatter([0], [0], c='b', label='primary')

    ax.legend(loc=1)
    ax.set_aspect('equal')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.show()


def binary_equipotential(**kwargs):
    """
    Plot function for descriptor = `equipotential` in function BinarySystem.plot(). This function plots crossections of
    surface Hill planes in xy, yz or zx plane

    :param kwargs: dict
                   keywords: plane = 'xy' - plane in which surface Hill plane is calculated, planes: 'xy', 'yz', 'zx'
                             phase = 0 - photometric phase in which surface Hill plane is calculated
    :return:
    """
    x_label, y_label = 'x', 'y'
    if utils.is_plane(kwargs['plane'], 'yz'):
        x_label, y_label = 'y', 'z'
    elif utils.is_plane(kwargs['plane'], 'zx'):
        x_label, y_label = 'x', 'z'

    x_primary, y_primary = kwargs['points_primary'][:, 0], kwargs['points_primary'][:, 1]
    x_secondary, y_secondary = kwargs['points_secondary'][:, 0], kwargs['points_secondary'][:, 1]

    f = plt.figure()
    ax = f.add_subplot(111)
    ax.plot(x_primary, y_primary, label='primary')
    ax.plot(x_secondary, y_secondary, label='secondary')
    lims = ax.get_xlim() - np.mean(ax.get_xlim())
    ax.set_ylim(lims)
    ax.set_aspect('equal', 'box')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend(loc=1)
    ax.grid()
    plt.show()


def binary_mesh(**kwargs):
    """
    Plot function for descriptor `mesh`, plots surface mesh of binary star in BinaryStar system

    :param kwargs: dict
                   keywords: `phase`: np.float - phase in which system is plotted default value is 0
                             `components_to_plot`: str - decides which argument to plot, choices: `primary`, secondary`
                                                         , `both`, default is `both`
    :return:
    """
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_aspect('equal')
    ax.elev = 90 - kwargs['inclination']
    ax.azim = kwargs['azimuth']
    if kwargs['components_to_plot'] in ['primary', 'both']:
        ax.scatter(kwargs['points_primary'][:, 0], kwargs['points_primary'][:, 1], kwargs['points_primary'][:, 2], s=5,
                   label='primary', alpha=1.0)
    if kwargs['components_to_plot'] in ['secondary', 'both']:
        ax.scatter(kwargs['points_secondary'][:, 0], kwargs['points_secondary'][:, 1], kwargs['points_secondary'][:, 2],
                   s=2, label='secondary', alpha=1.0)
    ax.legend(loc=1)

    x_min, x_max = 0, 0
    if kwargs['components_to_plot'] == 'both':
        x_min = np.min(kwargs['points_primary'][:, 0])
        x_max = np.max(kwargs['points_secondary'][:, 0])
    elif kwargs['components_to_plot'] == 'primary':
        x_min = np.min(kwargs['points_primary'][:, 0])
        x_max = np.max(kwargs['points_primary'][:, 0])
    elif kwargs['components_to_plot'] == 'secondary':
        x_min = np.min(kwargs['points_secondary'][:, 0])
        x_max = np.max(kwargs['points_secondary'][:, 0])

    limit = (x_max - x_min) / 2
    ax.set_xlim3d(x_min, x_max)
    ax.set_ylim3d(-limit, limit)
    ax.set_zlim3d(-limit, limit)

    if kwargs['plot_axis']:
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
    else:
        ax.set_axis_off()
    plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    plt.show()


def binary_wireframe(**kwargs):
    to_plot = kwargs.pop("components_to_plot")
    points_primary, faces_primary = kwargs.get("points_primary"), kwargs.get("primary_triangles")
    points_secondary, faces_secondary = kwargs.get("points_secondary"), kwargs.get("secondary_triangles")

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_aspect('equal')
    ax.elev = 90.0 - kwargs['inclination']
    ax.azim = kwargs['azimuth']

    if to_plot == 'primary':
        if points_primary is None or faces_primary is None:
            raise ValueError("missing primary faces or/and points")

        plot = ax.plot_trisurf(points_primary[:, 0], points_primary[:, 1], points_primary[:, 2],
                               triangles=faces_primary, antialiased=True, shade=False, color='none')

    elif to_plot == 'secondary':
        if points_secondary is None or faces_secondary is None:
            raise ValueError("missing secondary faces or/and points")

        plot = ax.plot_trisurf(points_secondary[:, 0], points_secondary[:, 1], points_secondary[:, 2],
                               triangles=faces_secondary, antialiased=True, shade=False, color='none')

    elif to_plot == 'both':
        if points_primary is None or faces_primary is None or points_secondary is None or faces_secondary is None:
            raise ValueError("missing primary or/and secondary faces or/and points")

        points = np.concatenate((points_primary, points_secondary), axis=0)
        triangles = np.concatenate((faces_primary, faces_secondary + np.shape(points_primary)[0]), axis=0)

        plot = ax.plot_trisurf(points[:, 0], points[:, 1], points[:, 2], triangles=triangles, antialiased=True,
                               shade=False, color='none')

    else:
        raise ValueError('invalid value of keyword argument `components_to_plot`, '
                         'expected values are: `primary`, `secondary` or `both`')

    plot.set_edgecolor('black')

    x_min, x_max = 0, 0
    if to_plot == 'both':
        x_min = np.min(points_primary[:, 0])
        x_max = np.max(points_secondary[:, 0])
    elif to_plot == 'primary':
        x_min = np.min(points_primary[:, 0])
        x_max = np.max(points_primary[:, 0])
    elif to_plot == 'secondary':
        x_min = np.min(points_secondary[:, 0])
        x_max = np.max(points_secondary[:, 0])

    limit = (x_max - x_min) / 2
    ax.set_xlim3d(x_min, x_max)
    ax.set_ylim3d(-limit, limit)
    ax.set_zlim3d(-limit, limit)
    if kwargs['plot_axis']:
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
    else:
        ax.set_axis_off()
    plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    plt.show()


def binary_surface(**kwargs):
    """
    todo: add all possibnble kwargs to docstring
    :param kwargs:
    :return:
    """
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_aspect('equal')
    ax.elev = 90 - kwargs['inclination']
    ax.azim = kwargs['azimuth']

    points_primary = kwargs.get('points_primary')
    points_secondary = kwargs.get('points_secondary')
    faces_primary = kwargs.get('primary_triangles')
    faces_secondary = kwargs.get('secondary_triangles')
    color_map = kwargs.pop('colormap')

    basic_colors = ['r', 'g']

    to_plot = kwargs.pop('components_to_plot')
    morphology = kwargs.pop('morphology')

    if to_plot == 'primary':
        if points_primary is None or faces_primary is None:
            raise ValueError("missing primary faces or/and points")

        plot = ax.plot_trisurf(
            points_primary[:, 0], points_primary[:, 1],
            points_primary[:, 2], triangles=kwargs['primary_triangles'],
            antialiased=True, shade=False, color=basic_colors[0])

        if kwargs.get('normals'):
            ax.quiver(
                kwargs['primary_centres'][:, 0], kwargs['primary_centres'][:, 1], kwargs['primary_centres'][:, 2],
                kwargs['primary_arrows'][:, 0], kwargs['primary_arrows'][:, 1], kwargs['primary_arrows'][:, 2],
                color='black', length=0.05)

    elif to_plot == 'secondary':
        if points_secondary is None or faces_secondary is None:
            raise ValueError("missing secondary faces or/and points")

        plot = ax.plot_trisurf(points_secondary[:, 0], points_secondary[:, 1],
                               points_secondary[:, 2], triangles=kwargs['secondary_triangles'],
                               antialiased=True, shade=False, color=basic_colors[0])

        if kwargs.get('normals'):
            ax.quiver(kwargs['secondary_centres'][:, 0], kwargs['secondary_centres'][:, 1],
                      kwargs['secondary_centres'][:, 2],
                      kwargs['secondary_arrows'][:, 0], kwargs['secondary_arrows'][:, 1],
                      kwargs['secondary_arrows'][:, 2],
                      color='black', length=0.05)

    elif to_plot == 'both':
        if points_primary is None or faces_primary is None or points_secondary is None or faces_secondary is None:
            raise ValueError("missing primary or/and secondary faces or/and points")

        if morphology == 'over-contact':
            points = np.concatenate((points_primary, points_secondary), axis=0)
            triangles = np.concatenate((faces_primary, faces_secondary + np.shape(points_primary)[0]), axis=0)

            plot = ax.plot_trisurf(points[:, 0], points[:, 1], points[:, 2], triangles=triangles,
                                   antialiased=True, shade=False)
            plot.set_facecolors(np.append(color_map["primary"], color_map["secondary"], axis=0))
        else:
            plot1 = ax.plot_trisurf(points_primary[:, 0], points_primary[:, 1],
                                    points_primary[:, 2], triangles=faces_primary,
                                    antialiased=True, shade=False)
            plot2 = ax.plot_trisurf(points_secondary[:, 0], points_secondary[:, 1],
                                    points_secondary[:, 2], triangles=faces_secondary,
                                    antialiased=True, shade=False)

            plot1.set_facecolors(color_map["primary"])
            plot2.set_facecolors(color_map["secondary"])

        if kwargs.get('normals'):
            centres = np.concatenate((kwargs['primary_centres'], kwargs['secondary_centres']), axis=0)
            arrows = np.concatenate((kwargs['primary_arrows'], kwargs['secondary_arrows']), axis=0)

            ax.quiver(centres[:, 0], centres[:, 1], centres[:, 2],
                      arrows[:, 0], arrows[:, 1], arrows[:, 2],
                      color='black', length=0.05)

    else:
        raise ValueError('invalid value of keyword argument `components_to_plot`\n'
                         'expected values are: `primary`, `secondary` or `both`')

    if kwargs.get('edges', False):
        if to_plot == 'both' and morphology != 'over-contact':
            plot1.set_edgecolor('black')
            plot2.set_edgecolor('black')
        else:
            plot.set_edgecolor('black')

    x_min, x_max = 0, 0
    if to_plot == 'both':
        x_min = np.min(points_primary[:, 0])
        x_max = np.max(points_secondary[:, 0])
    elif to_plot == 'primary':
        x_min = np.min(points_primary[:, 0])
        x_max = np.max(points_primary[:, 0])
    elif to_plot == 'secondary':
        x_min = np.min(points_secondary[:, 0])
        x_max = np.max(points_secondary[:, 0])

    limit = (x_max - x_min) / 2
    ax.set_xlim3d(x_min, x_max)
    ax.set_ylim3d(-limit, limit)
    ax.set_zlim3d(-limit, limit)

    if kwargs['plot_axis']:
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
    else:
        ax.set_axis_off()

    plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    plt.show()


def equipotential_single_star(**kwargs):
    """
    Plot function for descriptor = `equipotential` in function SingleSystem.plot(). Calculates zx plane crossection of
    equipotential surface.

    :param kwargs: dict:
                   keywords: `axis_unit` = astropy.units.solRad - unit in which axis will be displayed, please use
                                                               astropy.units format, default unit is solar radius
    :return:
    """
    x, y = kwargs['points'][:, 0], kwargs['points'][:, 1]

    unit = str(kwargs['axis_unit'])
    x_label, y_label = r'x/' + unit, r'y/' + unit

    f = plt.figure()
    ax = f.add_subplot(111)
    ax.grid()
    ax.plot(x, y)
    ax.set_aspect('equal', 'box')
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.show()


def single_star_mesh(**kwargs):
    """
    Plot function for descriptor `mesh`, plots surface mesh of star in SingleStar system

    :param kwargs: dict
                   keywords:`axis_unit` = astropy.units.solRad - unit in which axis will be displayed, please use
                                                                 astropy.units format, default unit is solar radius
    :return:
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.elev = 90 - kwargs['inclination']
    ax.azim = kwargs['azimuth']

    ax.scatter(kwargs['mesh'][:, 0], kwargs['mesh'][:, 1], kwargs['mesh'][:, 2], s=2)
    ax.set_xlim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])
    ax.set_ylim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])
    ax.set_zlim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])
    ax.set_aspect('equal', adjustable='box')
    if kwargs['plot_axis']:
        unit = str(kwargs['axis_unit'])
        x_label, y_label, z_label = r'x/' + unit, r'y/' + unit, r'z/' + unit
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_zlabel(z_label)
    else:
        ax.set_axis_off()
    plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    plt.show()


def single_star_wireframe(**kwargs):
    """
    Plot function for descriptor `wireframe` in SingleSystem, plots wireframe model of single system star

    :param kwargs: `axis_unit` = astropy.units.solRad - unit in which axis will be displayed, please use
                                                                 astropy.units format, default unit is solar radius

    :return:
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.elev = 90 - kwargs['inclination']
    ax.azim = kwargs['azimuth']

    star_plot = ax.plot_trisurf(kwargs['mesh'][:, 0], kwargs['mesh'][:, 1], kwargs['mesh'][:, 2],
                                triangles=kwargs['triangles'], antialiased=True, color='none')
    star_plot.set_edgecolor('black')

    ax.set_xlim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])
    ax.set_ylim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])
    ax.set_zlim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])
    ax.set_aspect('equal', adjustable='box')
    if kwargs['plot_axis']:
        unit = str(kwargs['axis_unit'])
        x_label, y_label, z_label = r'x/' + unit, r'y/' + unit, r'z/' + unit
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_zlabel(z_label)
    else:
        ax.set_axis_off()
    plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    plt.show()


def single_star_surface(**kwargs):
    """
    Plot function for descriptor `surface` in SingleSystem plot function, plots surface of star in SingleStar system

    :param kwargs: `axis_unit` - astropy.units.solRad : unit in which axis will be displayed, please use
                                                        astropy.units format, default unit is solar radius
                   `edges` - bool: if True edges of surface faces are visible
                   `normals` - bool: if True surface faces outward facing normals are visible
                   `colormap` - string: `temperature` - displays temperature surface colormap
                                        `gravity_acceleration` - displays gravity acceleration colormap

    :return:
    """
    fig = plt.figure(figsize=(7, 7))
    ax = axes3d.Axes3D(fig)
    ax.set_aspect('equal')
    ax.elev = 90 - kwargs['inclination']
    ax.azim = kwargs['azimuth']

    points, faces = kwargs.pop('mesh'), kwargs.pop('triangles')
    color_map = kwargs.pop('colormap')

    star_plot = ax.plot_trisurf(points[:, 0], points[:, 1], points[:, 2],
                                triangles=faces, antialiased=True, shade=False, alpha=1)
    if kwargs['edges']:
        star_plot.set_edgecolor('black')

    if kwargs['normals']:
        arrows = ax.quiver(kwargs['centres'][:, 0], kwargs['centres'][:, 1], kwargs['centres'][:, 2],
                           kwargs['arrows'][:, 0], kwargs['arrows'][:, 1], kwargs['arrows'][:, 2], color='black',
                           length=0.1 * kwargs['equatorial_radius'])

    star_plot.set_facecolors(color_map)

    ax.set_xlim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])
    ax.set_ylim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])
    ax.set_zlim3d(-kwargs['equatorial_radius'], kwargs['equatorial_radius'])

    if kwargs['plot_axis']:
        unit = str(kwargs['axis_unit'])
        x_label, y_label, z_label = r'x/' + unit, r'y/' + unit, r'z/' + unit
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_zlabel(z_label)
    else:
         ax.set_axis_off()
    plt.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    plt.show()
