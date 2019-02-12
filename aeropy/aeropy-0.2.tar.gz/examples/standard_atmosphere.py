#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Example of the ISA model
"""


import numpy as np
import matplotlib.pyplot as plt
import aeropy.atmosphere.model


# Initialize
atmosphere = aeropy.atmosphere.model.ISA()
heights = np.linspace(0, 90*10**3, 100)
temperatures = []
pressures = []
densities = []

# Calculate
for height in heights:
    temperatures += [atmosphere.temperature(height)]
    pressures += [atmosphere.pressure(height)]
    densities += [atmosphere.density(height)]

# Plot
plt.figure()
plt.title('international standard atmosphere')
plt.ylabel('height (in m)')
plt.xlabel('temperature (in K)')
plt.plot(temperatures, heights)
plt.show()
plt.figure()
plt.title('international standard atmosphere')
plt.ylabel('height (in m)')
plt.xlabel('pressure (in Pa)')
plt.plot(pressures, heights)
plt.show()
plt.figure()
plt.title('international standard atmosphere')
plt.ylabel('height (in m)')
plt.xlabel('density (in kg/m^3)')
plt.plot(densities, heights)
plt.show()
