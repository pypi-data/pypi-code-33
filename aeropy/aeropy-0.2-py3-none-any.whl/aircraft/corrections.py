#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Some typical corrections related to aircraft design
"""


import numpy as np


def compressibility(CP0, M, method='Prandtl', gamma = 1.4):
    """Compressibility correction for the pressure coefficient"""

    # Sanity check
    if M == 1:
        return np.nan

    # Prandtl-Glauert method
    if method == 'Prandtl':
        CP1 = CP0 / np.sqrt(1-M**2)
    # Laitone method
    elif method == 'Laitone':
        CP1 = CP0 / (np.sqrt(1-M**2) + (M**2*(1+(gamma-1)/2*M**2)/2*np.sqrt(1-M**2)*CP0))
    # Karman-Tsien method
    elif method == 'Karman':
        CP1 = CP0 / (np.sqrt(1-M**2) + (M**2 / (1 + np.sqrt(1-M**2)))*CP0*0.5)
    else:
        CP1 = 0

    return CP1
