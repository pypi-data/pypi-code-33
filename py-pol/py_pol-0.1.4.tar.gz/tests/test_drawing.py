# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for drawing module"""

import datetime
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from numpy import matrix

from py_pol import degrees, eps, um
from py_pol.drawings import draw_on_poincare, draw_poincare_sphere
from py_pol.jones_matrix import Jones_matrix
from py_pol.jones_vector import Jones_vector
from py_pol.mueller import Mueller
from py_pol.stokes import Stokes

"""
PendingDeprecationWarning: the matrix subclass is not the recommended way to
represent matrices or deal with linear algebra
(see https://docs.scipy.org/doc/numpy/user/numpy-for-matlab-users.html).
Please adjust your code to use regular ndarray.
"""

newpath = "drawings"
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d_%H_%M_%S")
newpath = "{}_{}/".format(newpath, date)

if not os.path.exists(newpath):
    os.makedirs(newpath)


class TestDrawing(object):
    # def test_Stokes_inclass(self):
    #     s01 = Stokes('s0')
    #     s01.linear_light(angle=0, intensity=1)
    #     filename = '{}test_Stokes_inclass.png'.format(newpath)
    #     s01.draw_poincare(filename=filename)
    #     plt.legend()
    #     assert True
    #
    # def test_Stokes_1_point(self):
    #
    #     s01 = Stokes('s0')
    #     s01.linear_light(angle=0, intensity=1)
    #
    #     ax, fig = draw_poincare_sphere(
    #         stokes_points=s01,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='scatter',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #
    #     plt.legend()
    #     filename = '{}test_Stokes_1_point.png'.format(newpath)
    #     fig.savefig(filename)
    #     assert True
    #
    # def test_Stokes_list_classes(self):
    #
    #     Stokes_points1 = []
    #
    #     s01 = Stokes('s0')
    #     s01.linear_light(angle=0, intensity=1)
    #     print(s01)
    #     # Stokes_points.append(s01.M)
    #
    #     angles = np.linspace(0, 90 * degrees, 90)
    #
    #     for i, angle in enumerate(angles):
    #         s_rot = s01.rotate(angle=angle, keep=False, returns_matrix=False)
    #         Stokes_points1.append(s_rot)
    #
    #     ax, fig = draw_poincare_sphere(
    #         stokes_points=Stokes_points1,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='line',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #
    #     plt.legend()
    #     filename = '{}test_Stokes_list_classes.png'.format(newpath)
    #     fig.savefig(filename)
    #     assert True
    #
    # def test_Stokes_list_matrices(self):
    #
    #     Stokes_points2 = []
    #
    #     s02 = Stokes('s0')
    #     s02.general_carac_angles(
    #         alpha=45 * degrees,
    #         delay=45 * degrees,
    #         intensity=1,
    #         pol_degree=0.75)
    #     print(s02)
    #     # Stokes_points.append(s01.M)
    #
    #     angles = np.linspace(0, 90 * degrees, 90)
    #
    #     for i, angle in enumerate(angles):
    #         s_rot = s02.rotate(angle=angle, keep=False, returns_matrix=True)
    #         Stokes_points2.append(s_rot)
    #
    #     ax, fig = draw_poincare_sphere(
    #         stokes_points=Stokes_points2,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='line',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #
    #     plt.legend()
    #     filename = '{}test_Stokes_list_matrices.png'.format(newpath)
    #     fig.savefig(filename)
    #     assert True
    #
    # def test_Stokes_on_poincare(self):
    #     Stokes_points2 = []
    #
    #     s02 = Stokes('s0')
    #     s02.general_carac_angles(
    #         alpha=45 * degrees,
    #         delay=45 * degrees,
    #         intensity=1,
    #         pol_degree=0.75)
    #     print(s02)
    #     # Stokes_points.append(s01.M)
    #
    #     angles = np.linspace(0, 90 * degrees, 90)
    #
    #     for i, angle in enumerate(angles):
    #         s_rot = s02.rotate(angle=angle, keep=False, returns_matrix=True)
    #         Stokes_points2.append(s_rot)
    #
    #     ax, fig = draw_poincare_sphere(
    #         stokes_points=None,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='line',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #     ax, fig = draw_poincare_sphere(
    #         stokes_points=None,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='line',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #     draw_on_poincare(
    #         ax, Stokes_points2, kind='line', color='r', label='rotation')  #
    #     plt.legend()
    #     filename = '{}test_Stokes_on_poincare.png'.format(newpath)
    #     fig.savefig(filename)
    #     assert True

    def test_Ellipse_inclass(self):
        s01 = Stokes('s0')
        s01.linear_light(angle=0, intensity=1)
        filename = '{}test_Ellipse_inclass.png'.format(newpath)
        s01.draw_ellipse(filename=filename)
        assert True

    #
    # def test_Ellipse_1_point(self):
    #
    #     s01 = Ellipse('s0')
    #     s01.linear_light(angle=0, intensity=1)
    #
    #     ax, fig = draw_poincare_sphere(
    #         Ellipse_points=s01,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='scatter',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #
    #     plt.legend()
    #     filename = '{}test_Ellipse_1_point.png'.format(newpath)
    #     fig.savefig(filename)
    #     assert True
    #
    # def test_Ellipse_list_classes(self):
    #
    #     Ellipse_points1 = []
    #
    #     s01 = Ellipse('s0')
    #     s01.linear_light(angle=0, intensity=1)
    #     print(s01)
    #     # Ellipse_points.append(s01.M)
    #
    #     angles = np.linspace(0, 90 * degrees, 90)
    #
    #     for i, angle in enumerate(angles):
    #         s_rot = s01.rotate(angle=angle, keep=False, returns_matrix=False)
    #         Ellipse_points1.append(s_rot)
    #
    #     ax, fig = draw_poincare_sphere(
    #         Ellipse_points=Ellipse_points1,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='line',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #
    #     plt.legend()
    #     filename = '{}test_Ellipse_list_classes.png'.format(newpath)
    #     fig.savefig(filename)
    #     assert True
    #
    # def test_Ellipse_list_matrices(self):
    #
    #     Ellipse_points2 = []
    #
    #     s02 = Ellipse('s0')
    #     s02.general_carac_angles(
    #         alpha=45 * degrees,
    #         delay=45 * degrees,
    #         intensity=1,
    #         pol_degree=0.75)
    #     print(s02)
    #     # Ellipse_points.append(s01.M)
    #
    #     angles = np.linspace(0, 90 * degrees, 90)
    #
    #     for i, angle in enumerate(angles):
    #         s_rot = s02.rotate(angle=angle, keep=False, returns_matrix=True)
    #         Ellipse_points2.append(s_rot)
    #
    #     ax, fig = draw_poincare_sphere(
    #         Ellipse_points=Ellipse_points2,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='line',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #
    #     plt.legend()
    #     filename = '{}test_Ellipse_list_matrices.png'.format(newpath)
    #     fig.savefig(filename)
    #     assert True
    #
    # def test_Ellipse_on_poincare(self):
    #     Ellipse_points2 = []
    #
    #     s02 = Ellipse('s0')
    #     s02.general_carac_angles(
    #         alpha=45 * degrees,
    #         delay=45 * degrees,
    #         intensity=1,
    #         pol_degree=0.75)
    #     print(s02)
    #     # Ellipse_points.append(s01.M)
    #
    #     angles = np.linspace(0, 90 * degrees, 90)
    #
    #     for i, angle in enumerate(angles):
    #         s_rot = s02.rotate(angle=angle, keep=False, returns_matrix=True)
    #         Ellipse_points2.append(s_rot)
    #
    #     ax, fig = draw_poincare_sphere(
    #         Ellipse_points=None,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='line',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #     ax, fig = draw_poincare_sphere(
    #         Ellipse_points=None,
    #         angle_view=[45 * degrees, 45 * degrees],
    #         kind='line',
    #         color='r',
    #         label='rotation')  # 'line', 'scatter'
    #     draw_on_poincare(
    #         ax, Ellipse_points2, kind='line', color='r', label='rotation')  #
    #     plt.legend()
    #     filename = '{}test_Ellipse_on_poincare.png'.format(newpath)
    #     fig.savefig(filename)
    #     assert True


plt.show()
