'''
Substrate thermal noise class, in_herits from NoiseParent.

References:
--- [1] Thorne and Liu 2000 Phys.Rev. D 62 122002
    https://arxiv.org/pdf/gr-qc/0002055.pdf
--- [2] Bondu, Hello and Vinet 1998 Phys.Let. A 
    https://www.sciencedirect.com/science/article/pii/S0375960198004502

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from scipy.special import jn_zeros, jn
from magic import constants
import numpy as np


class SubstrateThermoElasticNoise(NoiseParent):

    def getNoise(self):
        return self.substrateThermoElastic()

    def substrateThermoElastic(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Mirror material
        mirror = params['substrate_material'].properties
        # Frequency range
        f = params['frequency']
        # ITM beam radius
        w_itm = params['itm_beam_radius']
        # ETM beam radius
        w_etm = params['etm_beam_radius']
        # Poisson ratio
        sig = mirror['sigma']
        # Arm length
        L = params['length']
        # Substrate temperature
        T = params['substrate_temperature']
        # Substrate mass density
        rho = params['substrate_mass_density']
        # Substrate thermal conductivity
        kap = mirror['k']
        # Substrate thermal expansion coefficient
        alp = mirror['alpha']
        # Substrate specific heat
        cm = mirror['C']

        # Assign constants
        # Boltzmann energy
        kbT = constants.kb * T

        # Non-corrected thermal strain
        # [1] eqn. 17
        S_0 = (8 * pow((1 + sig) * alp, 2) * kap * T * kbT) / (
            np.sqrt(2 * np.pi) * pow(cm * rho, 2))
        S_itm = S_0 / pow(w_itm / np.sqrt(2), 3)
        S_etm = S_0 / pow(w_etm / np.sqrt(2), 3)

        # TODO - this is very similar to the function in substratebrownian.
        # Combine externally?
        # Calculation for corrections for finite test masses
        def finiteMassCorrection(width):

            # Assign parameters
            a = params['mass_radius']
            h = params['mass_thickness']
            # Bessel zeroes
            z = jn_zeros(1, 300)
            j_0m = jn(0, z)

            r_0 = width / np.sqrt(2)
            k_m = z / a

            # [1] eqn. 35a
            Q_m = np.exp(-2 * k_m * h)
            # [1] eqn. 37
            p_m = np.exp(-pow(k_m * r_0, 2) / 4) / (np.pi * pow(a * j_0m, 2))
            # [1] eqns. 28, 32, 40
            c1 = -12*pow(a/h, 2)*sum(j_0m*p_m/pow(z, 2))/h \
                 + pow(2*h*np.pi*pow(a, 2), -1)
            # [1] eqn. 46
            c2 = (1 - Q_m) * ((1 - Q_m) * (1 + Q_m) + 8 * h * k_m * Q_m)
            c2 += 4 * pow(h * k_m, 2) * Q_m * (1 + Q_m)
            c2 *= k_m * pow(p_m * j_0m, 2) * (1 - Q_m)
            c2 = sum(c2 / pow(pow(1 - Q_m, 2) - 4 * pow(h * k_m, 2) * Q_m, 2))
            c2 += h * pow(c1 / (1 + sig), 2)

            return c2 * pow(np.sqrt(2 * np.pi) * r_0, 3) * pow(a, 2)

        # Implement corrections from [1] to original calculations from [2]
        S_itm *= finiteMassCorrection(w_itm)
        S_etm *= finiteMassCorrection(w_etm)

        # 2 mirrors of each type
        # Noise power spectral density
        n = 2 * (S_itm + S_etm) / pow(2 * np.pi * f * L, 2)

        return np.sqrt(n)
