#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Aircraft geometry calculations
"""


import numpy as np


def lambda_qc(lambda_le, b, taper, c_root):
    """Quarter chord sweep calculator"""
    x = b/2 * np.tan(lambda_le) + 0.25*taper*c_root - 0.25*c_root
    lambda_qc = np.arctan(2 * x / b)
    return lambda_qc
