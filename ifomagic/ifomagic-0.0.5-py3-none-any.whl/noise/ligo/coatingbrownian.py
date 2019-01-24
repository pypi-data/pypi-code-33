'''
Coating Brownian noise class, in_herits from NoiseParent.

References:
--- [1] M Harry et al. 2007 Class. Quantum Grav. 24 405
   https://arxiv.org/pdf/gr-qc/0610004.pdf
--- [2] Nakagawa et al. 2001 Phys.Rev. D 65 102001
   https://arxiv.org/ftp/gr-qc/papers/0105/0105046.pdf
--- [3] Martin I and Reid S. 2012 
   https://www.researchgate.net/publication/258734551_
   Optical_Coatings_and_Thermal_Noise_in_Precision_Measurement


MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from magic import constants
import numpy as np


class CoatingBrownianNoise(NoiseParent):

    def getNoise(self):
        return self.coatbrownian()

    def coatbrownian(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency
        f = params['frequency']
        # Arm length
        L = params['length']
        # ITM beam radius
        br_itm = params['itm_beam_radius']
        # ETM beam radius
        br_etm = params['etm_beam_radius']
        # Optical thickness of ITM coating
        cot_itm = params['itm_coating_optical_thickness']
        # Optical thickness of ETM coating
        cot_etm = params['etm_coating_optical_thickness']

        def getCoatingBrownian(br, cot):

            # Assign parameters
            # Substrate temperature
            T_s = params['substrate_temperature']
            # Laser beam wavelength
            lam = params['wavelength']

            # Substrate
            mirror = params['substrate_material'].properties
            # Mirror Young's modulus
            Y_s = mirror['Y']
            # Mirror Poisson ratio
            sig_s = mirror['sigma']

            # Coating
            # High refractive index
            # Young's modulus
            Y_h = params['coating_highn_Y']
            # Poisson ratio
            sig_h = params['coating_highn_sigma']
            #
            phi_h = params['coating_highn_phi']
            # Refractive index
            i_h = params['coating_highn_index']
            # Low refractive index
            Y_l = params['coating_lown_Y']
            # Poisson ratio
            sig_l = params['coating_lown_sigma']
            #
            phi_l = params['coating_lown_phi']
            # Refractive index
            i_l = params['coating_lown_index']

            # Assign constants
            # Boltzmann energy
            kBT = constants.kb * T_s

            # Thickness of each coating material
            d_l = sum(cot[::2]) * lam / i_l
            d_h = sum(cot[1::2]) * lam / i_h
            # Coating
            d_c = d_l + d_h

            L_l = d_l * phi_l
            L_h = d_h * phi_h
            L_all = [L_l + L_h, L_l, L_h]

            # [1]
            Y_perp = d_c / (d_h / Y_h + d_l / Y_l)
            phi_perp = Y_perp / d_c * (d_l * phi_l / Y_l + d_h * phi_h / Y_h)
            Y_para = 1 / d_c * (Y_h * d_h + Y_l * d_l)
            phi_para = 1 / (d_c * Y_para) * (
                Y_l * phi_l * d_l + Y_h * phi_h * d_h)

            sig_1 = 1 / 2 * (sig_h + sig_l)

            sig_2 = (sig_h * Y_h * d_h + sig_l * Y_l * d_l) / (
                Y_h * d_h + Y_l * d_l)

            # Brownian thermal noise
            # Split into components for ease of understanding
            bn_a = d_c * (1 - pow(sig_s, 2)) / (np.pi * pow(br, 2))

            bn_ba = 1 / (Y_perp * (1 - pow(sig_s, 2)))
            bn_bb = 2 * pow(sig_2, 2)
            bn_bc = Y_para / (pow(Y_perp, 2) * (1 - pow(sig_s, 2)) *
                              (1 - sig_1))
            bn_b = phi_perp * (bn_ba - bn_bb * bn_bc)

            bn_ca = (phi_para - phi_perp)
            bn_cb = Y_para * sig_2 * (1 - 2 * sig_s)
            bn_cc = Y_perp * Y_s * (1 - sig_1) * (1 - sig_s)
            bn_c = bn_ca * bn_cb / bn_cc

            bn_da = Y_para * (1 + sig_s) * pow(1 - 2 * sig_s, 2)
            bn_db = pow(Y_s, 2) * (1 - pow(sig_1, 2)) * (1 - sig_s)
            bn_d = phi_para * bn_da / bn_db

            # Noise as power spectrum
            bn = 4 * kBT * bn_a * (bn_b + bn_c + bn_d) / (2 * np.pi * f)

            return bn

        n_itm = getCoatingBrownian(br_itm, cot_itm)
        n_etm = getCoatingBrownian(br_etm, cot_etm)

        # Noise power spectral density
        n = 2 * (n_itm + n_etm) / pow(L, 2)

        return np.sqrt(n)
