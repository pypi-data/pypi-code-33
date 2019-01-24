'''
Residual gas noise class, in_herits from NoiseParent.

References:
--- [1] R Weiss et al. 1995 LIGO-T952011-00-R
      https://dcc.ligo.org/LIGO-T952011/public

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from magic import constants
import numpy as np


class ResidualGasNoise(NoiseParent):

    def getNoise(self):
        return self.gas()

    def gas(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency range
        f = params['frequency']
        # Arm length
        L = params['length']
        # Laser wavelength
        lam = params['wavelength']
        # Temperature of detector
        T = params['temperature']
        # Residual gas pressure
        P = params['residual_gas_pressure']
        # Residual gas mass of one particle
        M = params['residual_gas_mass']
        # Curvature of ITM
        r_itm = params['itm_curvature']
        # Curvature of ETM
        r_etm = params['etm_curvature']
        # Polarisability of gas
        alpha = params['residual_gas_polarizability']
        # Size of Gaussian beam waist
        waist = params['gaussian_beam_waist']
        # ITM position relative to waist
        z_itm = params['itm_position_wrt_waist']
        # ETM position relative to waist
        z_etm = params['etm_position_wrt_waist']

        # Assign constants
        # Boltzmann constant
        k = constants.kb
        # No. density of gas
        rho = P / (k * T)
        # Average velocity of gas
        v_0 = np.sqrt(2 * k * T / M)

        # Rayleigh range
        z_R = np.pi * pow(waist, 2) / lam

        log_etm = np.log(z_etm + np.sqrt(pow(z_etm, 2) + pow(z_R, 2)))
        log_itm = np.log(z_itm + np.sqrt(pow(z_itm, 2) + pow(z_R, 2)))

        # One-arm optical path length
        z_opl = (log_etm - log_itm) * z_R / waist - 2 * np.pi * L * f / v_0
        z_opl = z_opl * 4 * rho * pow(2 * np.pi * alpha, 2) / v_0
        # Get rid of negatives introduced by approximating to first order
        z_opl[z_opl < 0] = 0
        # Accumulate noise from both arms when converting to strain noise
        # Noise power spectral density
        n = 2 * z_opl / pow(L, 2)

        return np.sqrt(n)
