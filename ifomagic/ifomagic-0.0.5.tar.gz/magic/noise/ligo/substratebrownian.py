'''
Substrate Brownian noise class, in_herits from NoiseParent.

References:
--- [1] Thorne and Liu 2000 Phys.Rev. D 62 122002
    https://arxiv.org/pdf/gr-qc/0002055.pdf
--- [2] Bondu, Hello and Vincent 1998 Phys.Let. A
   https://www.sciencedirect.com/science/article/pii/S0375960198004502
--- [3] Hemptonstall et al. 2014 Class. Quantum Grav. 31 105006
   https://authors.library.caltech.edu/46365/1/0264-9381_31_10_105006.pdf

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from scipy.special import jn_zeros, jn
from magic import constants
import numpy as np


class SubstrateBrownianNoise(NoiseParent):

    def getNoise(self):
        return self.substrateBrownianThermal()

    def substrateBrownianThermal(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency
        f = params['frequency']
        # ITM beam radius
        w_itm = params['itm_beam_radius']
        # ETM beam radius
        w_etm = params['etm_beam_radius']
        # Mirror material
        mirror = params['substrate_material'].properties
        # Substrate Young's modulus
        Y = mirror['Y']
        # Poisson ratio
        sig = mirror['sigma']
        # Coefficient of freq dep term for bulk loss
        c2 = mirror['c2']
        # Frequency dependence of loss
        n = mirror['loss_exp']
        # Surface loss limit
        alp_s = mirror['surf_loss_lim']
        # Arm length
        L = params['length']

        # Assign constants
        # Boltzmann energy
        kbT = constants.kb * params['substrate_temperature']

        # TODO - this is very similar to the function in substratethermoelastic.
        # Combine externally?
        # Strain in corrected finite mass
        # (Brownian-specific)
        def finiteMassCorrected(width):

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

            # [1] eqn. 53, [2]
            U_m = (1 - Q_m) * (1 + Q_m) + 4 * h * k_m * Q_m
            U_m = U_m / (pow(1 - Q_m, 2) - 4 * pow(k_m * h, 2) * Q_m)

            # [1] eqn. 57
            x = np.exp(-pow(z * r_0 / a, 2) / 4)
            s = sum(x / (pow(z, 2) * j_0m))

            # [1] eqn. 56, [2] eqn. 3
            U_0 = sum(U_m * pow(x, 2) / (z * pow(j_0m, 2)))
            U_0 *= (1 - sig) * (1 + sig) / (np.pi * a * Y)

            # [1] eqn. 28
            p_0 = 1 / (np.pi * pow(a, 2))

            # [1] eqn. 54
            dU = pow(np.pi * pow(h, 2) * p_0, 2)
            dU += 12 * np.pi * pow(h, 2) * p_0 * sig * s
            dU += 72 * (1 - sig) * pow(s, 2)
            dU *= pow(a, 2) / (6 * np.pi * pow(h, 3) * Y)

            # Finite: [1] eqn. 58, following [2] eqn. 31
            a_ftm = dU + U_0
            # Infinite: [1] eqn. 59
            a_itm = (1 - pow(sig, 2)) / (2 * np.sqrt(2 * np.pi) * Y * r_0)

            # Ratio (correction for finite mirror)
            c_ftm = a_ftm / a_itm

            return c_ftm, a_ftm

        # Bulk substrate contribution
        phi_bulk = c2 * pow(f, n)
        c_itm, a_itm = finiteMassCorrected(w_itm)
        c_etm, a_etm = finiteMassCorrected(w_etm)
        c_bulk = 8 * kbT * (a_itm + a_etm) * phi_bulk / (2 * np.pi * f)

        # Surface loss contributions
        C_setm = alp_s * (1 - 2 * sig) / ((
            1 - sig) * Y * np.pi * pow(w_etm, 2))
        C_sitm = alp_s * (1 - 2 * sig) / ((
            1 - sig) * Y * np.pi * pow(w_itm, 2))
        C_surf = 8 * kbT * (C_setm + C_sitm) / (2 * np.pi * f)

        # 2 mirrors of each type
        # Noise power spectral density
        n = 2 * (C_surf + c_bulk) / pow(L, 2)

        return np.sqrt(n)