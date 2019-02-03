# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for drawing module"""

import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from numpy import matrix

from py_pol import degrees, eps, um
from py_pol.drawings import draw_on_poincare, draw_poincare_sphere
from py_pol.jones_matrix import Jones_matrix
from py_pol.jones_vector import Jones_vector
from py_pol.mueller import Mueller
from py_pol.stokes import Stokes


def test_Stokes_1_point():

    s01 = Stokes('s0')
    s01.linear_light(angle=0, intensity=4)
    angle_view_0 = [45 * degrees, 45 * degrees]

    ax, fig = draw_poincare_sphere(
        stokes_points=s01,
        angle_view=angle_view_0,
        kind='scatter',
        color='r',
        label='rotation')  # 'line', 'scatter'

    plt.legend()
    fig.savefig('drawings/test_Stokes_1_point.png')


test_Stokes_1_point()
plt.show()
