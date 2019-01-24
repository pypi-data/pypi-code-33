'''
Suspension thermal noise class, in_herits from NoiseParent. 

References:
--- [1] A V Cumming et al. 2012 Class. Quantum Grav. 29 035003
    http://iopscience.iop.org/article/10.1088/0264-9381/29/3/035003/pdf

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from magic import constants
import numpy as np


class SuspensionThermalNoise(NoiseParent):

    def getNoise(self):
        return self.suspensionThermal()

    def suspensionThermal(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency range
        f = params['frequency']
        # Suspension temperature
        T = params['suspension_temperature']
        # Vertical to beamline coupling angle
        theta = params['suspension_VH_coupling_theta']
        # Arm length
        L = params['length']
        # Horizontal suspension transfer function
        F_h = params['suspension_hforce']
        # Vertical suspension transfer function
        F_v = params['suspension_vforce']
        # Number of suspension stages
        n_stages = len(params['mirror_mass'])
        # Signal angular frequency
        w = params['signal_omega']

        # Assign constants
        # Stefan-Boltzmann constant
        k = constants.kb

        # Check whether stages have differing temperatures
        identical = True
        for t, temp in enumerate(T):
            if t == 0:
                pass
            else:
                if temp != T[t - 1]:
                    identical = False
                    break

        if identical:

            # Horizontal suspension transfer function
            F_h = F_h['fully_lossy']
            # Vertical suspension transfer function
            F_v = F_v['fully_lossy']

            # Get scalar T
            T = sum(T) / len(T)

            # Transfer functions to beam line motion
            dxdF = F_h + pow(theta, 2) * F_v
            # Thermal noise for one suspension stage
            n = 4 * k * T * abs(np.imag(dxdF)) / w

        else:

            # Horizontal suspension transfer function
            F_h = F_h['singly_lossy'][:, :]
            # Vertical suspension transfer function
            F_v = F_v['singly_lossy'][:, :]

            # Add contributions from all stages
            n = np.zeros((1, f.size))
            dxdF = np.zeros(F_h.shape, dtype=complex)

            for i in range(len(T)):

                # Transfer function to beam line motion
                # Square theta, rotate into suspension and then beamline basis
                dxdF[i, :] = F_h[i, :] + pow(theta, 2) * F_v[i, :]

                # Thermal noise for one suspension stage
                n = n + 4 * k * T[i] * abs(np.imag(dxdF[i, :])) / w

        # Noise power spectral density
        n = np.squeeze(n_stages * n / pow(L, 2))

        return np.sqrt(n)
