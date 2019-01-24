'''
Carrier density ITM noise class for Voyager, inherits from NoiseParent.

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


class CarrierDensityNoise(NoiseParent):

    def getNoise(self):
        return self.carrierdensity()

    def carrierdensity(self):

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

        # Load Voyager-on_ly parameters
        # Mirror
        mirror = params['substrate_material'].properties
        # Electron diffusion rate
        electron_diffusion_rate = mirror['electron_diffusion']
        # Hole diffusion rate
        hole_diffusion_rate = mirror['hole_diffusion']
        # Effective mass of electron
        mass_electron = mirror['electron_effective_mass']
        # Effective mass of hole
        mass_hole = mirror['hole_effective_mass']
        # Carrier density
        cd_density = mirror['carrier_density']
        # Dependence of refractive index on electron carrier density
        gamma_electron = mirror['electron_index_gamma']
        # Dependence of refractive index on hole carrier density
        gama_hole = mirror['hole_index_gamma']
        # Signal angular frequency
        w = params['signal_omega']
        # Finesse
        F = params['finesse']

        # Assign constants
        # Boltzmann energy
        kbT = constants.kb * T_s
        # Speed of light
        c = constants.c

        # Do calculations
        FSR = c / 2 / L
        cav_pol = FSR / 2 / F
        g_phase = 2 * F / np.pi

        int_elec = np.array([integrate.quad(lambda k: \
             integrand.calculate(k, om, electron_diffusion_rate, w_itm), 0, np.inf)[0]\
                    for om in w])

        int_hole = np.array([integrate.quad(lambda k: \
             integrand.calculate(k, om, hole_diffusion_rate, w_itm), 0, np.inf)[0]\
                    for om in w])

        def PSDCD(gam, m, int_):
            return 2 / np.pi * H * pow(gam, 2) * cd_density * int_

        psd_electron = PSDCD(gamma_electron, mass_electron, int_elec)
        psd_hole = PSDCD(gama_hole, mass_hole, int_hole)

        # Noise power spectral density
        # Two input mirrors
        n = 2 * (psd_electron + psd_hole) / pow(g_phase * L, 2)

        # Return amplitude spectral density

        return np.sqrt(n)