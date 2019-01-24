'''
Thermo-refractive ITM noise class, in_herits from NoiseParent.

Strain noise arising from thermorefractive fluctuations in semiconductor
substrates, to be used for Voyager.

References:
--- [1] P1400084 Heinert et al

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic import constants
import scipy.integrate as integrate
from magic.noise import NoiseParent
from magic.utils.ligo import integrand
import numpy as np


class ThermoRefractiveNoise(NoiseParent):

    def getNoise(self):
        return self.ThermoRefractiveITM()

    def ThermoRefractiveITM(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency
        f = params['frequency']
        # ITM beam radius
        w_itm = params['itm_beam_radius']
        # Arm length
        L = params['length']
        # Substrate temperature
        T_s = params['substrate_temperature']
        # Mass thickness
        H = params['mass_thickness']
        # ITM transmittance
        T_itm = params['itm_transmittance']
        # Substrate mass density
        rho = params['substrate_mass_density']
        # Mirror
        mirror = params['substrate_material'].properties
        # Rate of change of refractive index wrt temperature
        bet = mirror['dn_dT']
        # Substrate specific heat
        C = mirror['C']
        # Substrate thermal conductivity
        kap = mirror['k']
        # Signal angular frequency
        w = params['signal_omega']

        # Assign constants
        # Boltzmann energy
        kbT = constants.kb * T_s
        # Speed of light
        c = constants.c

        # Do calculations
        FSR = c / 2 / L
        # Internal finesse calculation
        F = 2 * np.pi / T_itm
        g_phase = 2 * F / np.pi

        inte = np.array([integrate.quad(lambda k: \
               integrand.calculate(k, om, kap/(rho*C), w_itm), 0, np.inf)[0]\
                     for om in w])

        def PSDTR(bet, T_s, int_):
            return 2/np.pi*H*pow(bet, 2)*kbT*T_s/(rho*C)*int_

        # Power spectral density
        # Two input mirrors
        n = 2 * PSDTR(bet, T_s, inte) / pow(g_phase * L, 2)

        return np.sqrt(n)