'''
Calculates the coating and substrate optical thicknesses.

References:
--- [1]  Nakagawa et al. 2001 Phys.Rev. D 65 102001
   https://arxiv.org/ftp/gr-qc/papers/0105/0105046.pdf

MAGIC
@author: Isobel
'''
from copy import deepcopy
import numpy as np


def calculate(ifo):

    # Assign parameters
    params = deepcopy(ifo.parameters)

    # Assign parameters
    mirror = params['substrate_material'].properties
    n_s = mirror['r_index']
    n_l = params['coating_lown_index']
    n_h = params['coating_highn_index']
    T_i = params['itm_transmittance']
    T_e = params['etm_transmittance']
    d_li = params['itm_coating_lown_thickness']
    d_le = params['etm_coating_lown_thickness']
    d_maxi = params['itm_coating_max_thickness']
    d_maxe = params['etm_coating_max_thickness']

    verbose = ifo.verbose

    def getCoatRefl(d_opt):

        n_layer = d_opt.size

        # Refractive index of input, coating, and output materials
        n_all = np.zeros(n_layer + 2)
        # Vacuum input
        n_all[0] = 1
        n_all[1::2] = n_l
        n_all[2::2] = n_h
        # Substrate output
        n_all[-1] = n_s

        # Reflectivity of each interface
        r_inter = (n_all[:-1] - n_all[1:]) / (n_all[:-1] + n_all[1:])

        # Combine layers as small FP cavities
        # Start with last reflectivity
        r_coat = r_inter[-1]
        for n in reversed(range(d_opt.size)):
            # One-way phase in this layer
            phi = 2 * np.pi * d_opt[n]
            # Accumulate reflectivity
            r_c = r_coat * np.exp(-2j * phi)
            r_coat = (r_inter[n] + r_c) / (1 + r_inter[n] * r_c)
        return r_coat

    def getDopt(T, d_l, d_max):

        # No. 1/4 - wave layers required (first guess)
        n_r = n_h / n_l
        a1 = (2 - T + 2 * np.sqrt(1 - T)) / (n_r * n_h * T)

        # No. doublets
        n_dblt = int(np.ceil(np.log(a1) / (2 * np.log(n_r))))

        # Search through n_dblt to find how many give T lower than req.
        d_h = 0.5 - d_l
        n_array = np.array([d_h])
        N = n_array.size

        def getTrans(n_dblt, d_tweak):

            d_opt = np.zeros(2 * n_dblt)
            d_opt[0] = d_max
            d_opt[1::2] = d_h
            d_opt[2::2] = d_l

            N_Tweak = d_tweak.size
            trans = np.zeros(N_Tweak)

            for n in range(N_Tweak):
                d_opt[-1] = d_tweak[n]
                r = getCoatRefl(d_opt)
                trans[n] = 1 - abs(pow(r, 2))

            return trans

        T_n = getTrans(n_dblt, n_array)

        while T_n < T and n_dblt > 1:
            # Remove doublets
            n_dblt -= 1
            T_n = getTrans(n_dblt, n_array)
        while T_n > T and n_dblt < 1E3:
            # Add doublets
            n_dblt += 1
            T_n = getTrans(n_dblt, n_array)

        # Tweak bottom layer
        def getTweak(d_scan, T, Nfit):

            T_n = getTrans(n_dblt, d_scan)
            pf = np.polyfit(d_scan, T_n - T, Nfit)
            rts = np.roots(pf)

            a = np.imag(rts) == 0 & (rts > 0)
            if not np.any(a):
                d_tweak = None
                T_d = 0
                return d_tweak, T_d

            d_tweak = np.real(np.min(rts[a]))

            # Compute T for this d_tweak
            T_d = getTrans(n_dblt, np.array([d_tweak]))
            return d_tweak, T_d

        delta = 0.01
        d_scan = np.arange(0, 0.25 + delta, delta)
        d_tweak = getTweak(d_scan, T, 5)[0]

        if not d_tweak:
            if n_s> n_l:
                raise Exception(
                    'Coating tweak layer not sufficient since n_s> n_l.')
            else:
                raise Exception('Coating tweak layer not found.')

        # Get better result with linear fit
        delta = 0.001
        d_scan = np.linspace(d_tweak - 3 * delta, d_tweak + 3 * delta, 7)
        d_tweak, T_d = getTweak(d_scan, T, 3)

        # Remove negative values
        if d_tweak < 0.01:
            d_tweak = 0.01

        # Check the result
        error_magnitude = abs(np.log(T_d / T))

        if error_magnitude > 1E-3:
            if verbose:
                print('Coating tweak layer has %g%% error.' % error_magnitude)

        # Return d_opt vector
        d_opt = np.zeros((2 * n_dblt, 1))
        d_opt[0] = d_max
        d_opt[1::2] = d_h
        d_opt[2::2] = d_l
        d_opt[-1] = d_tweak

        return d_opt

    # Return ITM and ETM optical thickness
    ot_itm = getDopt(T_i, d_li, d_maxi)
    ot_etm = getDopt(T_e, d_le, d_maxe)

    return ot_itm, ot_etm
