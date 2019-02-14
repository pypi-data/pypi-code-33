#!/usr/bin/env python

"""
V1.0.0: Michele Cappellari, Oxford, 17 April 2018

"""

import numpy as np
import matplotlib.pyplot as plt

from jampy.mge_vcirc import mge_vcirc

def mge_vcirc_example():
    """
    Usage example for mge_vcirc()
    It takes a fraction of a second on a 2GHz computer
    
    """    
    # Realistic MGE galaxy surface brightness
    # 
    surf = np.array([39483, 37158, 30646, 17759, 5955.1, 1203.5, 174.36, 21.105, 2.3599, 0.25493])
    sigma = np.array([0.153, 0.515, 1.58, 4.22, 10, 22.4, 48.8, 105, 227, 525])
    qObs = np.array([0.57, 0.57, 0.57, 0.57, 0.57, 0.57, 0.57, 0.57, 0.57, 0.57])
    
    inc = 60. # Inclination in degrees
    mbh = 1e6 # BH mass in solar masses
    distance = 10. # Mpc
    rad = np.geomspace(0.1, 100, 25) # Radii in arscec where Vcirc has to be computed
    ml = 5.0 # Adopted M/L ratio
    
    vcirc = mge_vcirc(surf*ml, sigma, qObs, inc, mbh, distance, rad)

    plt.plot(rad, vcirc, '-o')
    plt.xlabel('R (arcsec)')
    plt.ylabel(r'$V_{circ}$ (km/s)')

#----------------------------------------------------------------------

if __name__ == '__main__':
    
    plt.clf()
    mge_vcirc_example()
    plt.pause(1)
