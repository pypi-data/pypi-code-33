#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Python codes to create airfoil shapes
"""


from .external.naca import naca

import numpy as np
import scipy.special as sp


def cst(coef_upper, coef_lower, n, finite_te=None, half_cosine_spacing=None):
    """
    Creates an airfoil shape based on CST airfoil coefficients
    """

    # x
    if half_cosine_spacing:
        betas = np.linspace(0.0, np.pi, n + 1)
        x = [(0.5 * (1.0 - np.cos(beta))) for beta in betas]
    else:
        x = np.linspace(0.0, 1.0, n + 1)

    # y
    if finite_te:
        zeta_upper = finite_te/2.0
        zeta_lower = -finite_te/2.0
    else:
        zeta_upper = 0.0
        zeta_lower = 0.0

    # Class function
    n1 = 0.5
    n2 = 1.0
    c = x**n1*(1.0-x)**n2

    # Shape function
    def shape(coef):
        nn = len(coef)
        s = np.sum([coef[i]*sp.binom(nn, i)*x**i*(1.0-x)**(nn-i) for i in range(nn)], axis=0)
        return s

    s_upper = shape(coef_upper)
    s_lower = shape(coef_lower)

    # CST function
    y_upper = c*s_upper + x*zeta_upper
    y_lower = c*s_lower + x*zeta_lower

    # Output
    x = np.append(x[::-1], x[1:])
    y = np.append(y_upper[::-1], y_lower[1:])

    return x, y
