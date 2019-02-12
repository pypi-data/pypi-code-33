#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Example demonstration of different compressibility corrections
"""


import numpy as np
import matplotlib.pyplot as plt
import aeropy.aircraft.corrections


# Vectorize correction for fastcomputing performance
correction = np.vectorize(aeropy.aircraft.corrections.compressibility)

# Set up example
mach = np.linspace(0, 1, 100)
prandtl = correction(1, mach, 'Prandtl')
laitone = correction(1, mach,'Laitone')
karman = correction(1, mach, 'Karman')

# Plot
plt.figure()
plt.title('pressure coefficient compressibility correction')
plt.xlabel('M')
plt.ylabel('correction factor')
plt.plot(mach, prandtl, label='Prandtl')
plt.plot(mach, laitone, label='Laitone')
plt.plot(mach, karman, label='Karman')
plt.legend()
plt.show()