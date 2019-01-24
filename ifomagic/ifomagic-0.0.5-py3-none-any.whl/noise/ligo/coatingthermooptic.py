'''
Coating thermo-optic noise class, in_herits from NoiseParent.

References:
--- [1] M Evans 2008 Phys.Rev. D 78 102003
	https://arxiv.org/pdf/0807.4774.pdf
--- [2] Braginskii

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from magic import constants
from scipy.special import jn_zeros, jn
import numpy as np


class CoatingThermoOpticNoise(NoiseParent):

   def getNoise(self):
      return self.coatthermooptic()

   def coatthermooptic(self):

      # Assign parameters
      params = deepcopy(self.ifo.parameters)
      # Frequency
      f = params['frequency']
      # Arm length
      L = params['length']
      # ITM beam radius
      w_itm = params['itm_beam_radius']
      # ETM beam radius
      w_etm = params['etm_beam_radius']
      # Optical thickness of ITM coating
      d_itm = params['itm_coating_optical_thickness']
      # Optical thickness of ETM coating
      d_etm = params['etm_coating_optical_thickness']

      # Function to get thermo-optic noise power spectra for single optic
      def getNoise(wb, d):

         # Laser light wavelength
         lam = params['wavelength']

         # Substrate:
         mirror = params['substrate_material'].properties
         # Temperature
         T_s = params['substrate_temperature']
         # Volumetric heat capacity
         C_s = mirror['C'] * params['substrate_mass_density']
         # Thermal conductivity
         K_s = mirror['k']
         # Refractive index
         n_s = mirror['r_index']
         # Young's modulus
         Y_s = mirror['Y']
         # Poisson ratio
         sig_s = mirror['sigma']
         # Thermal expansion coefficient
         alp_s = mirror['alpha']

         # Coating:
         # Low refractive index:
         # Thermal expansion coefficient
         alp_L = params['coating_lown_alpha']
         # Change in refractive index with temperature
         bet_L = params['coating_lown_beta']
         # Young's modulus
         Y_L = params['coating_lown_Y']
         # Poisson ratio
         sig_L = params['coating_lown_sigma']
         # Refractive index
         n_L = params['coating_lown_index']
         C_L = params['coating_lown_CV']
         K_L = params['coating_lown_thermal_conductivity']
         # High refractive index:
         # Thermal expansion coefficient
         alp_H = params['coating_highn_alpha']
         # Change in refractive index with temperature
         bet_H = params['coating_highn_beta']
         # Young's modulus
         Y_H = params['coating_highn_Y']
         # Poisson ratio
         sig_H = params['coating_highn_sigma']
         # Refractive index
         n_H = params['coating_highn_index']
         C_H = params['coating_highn_CV']
         K_H = params['coating_highn_thermal_conductivity']

         # Test mass radius
         R_s = params['mass_radius']
         # Test mass thickness
         H_s = params['mass_thickness']

         # Assign constants
         # Angular frequency
         w = params['signal_omega']
         # Boltzmann energy * temperature
         kbT2 = constants.kb * pow(T_s, 2)

         # Total number of layers
         n_layer = len(d)

         # Function to calculate the expansion ratio for a material with
         # a given Y and sigma
         def expansionRatio(Y, S):
            ce = ((1 + sig_s) / (1 - S)) * (((1 + S) / (1 + sig_s)) +
                                            (1 - 2 * sig_s) * Y / Y_s)
            return ce

         # Effective alpha
         aL = np.zeros((n_layer, 1))
         aL[::2] = alp_L * expansionRatio(Y_L, sig_L)
         aL[1::2] = alp_H * expansionRatio(Y_H, sig_H)

         # Effective beta
         bL = np.zeros((n_layer, 1))
         bL[::2] = bet_L
         bL[1::2] = bet_H

         # Effective refractive index
         n_l = np.zeros((n_layer, 1))
         n_l[::2] = n_L
         n_l[1::2] = n_H

         # Geometrical thickness
         d_L= lam * d / n_l

         # Effective sigma c
         sL = np.zeros((n_layer, 1))
         sL[::2] = alp_L * (1 + sig_L) / (1 - sig_L)
         sL[1::2] = alp_H * (1 + sig_H) / (1 - sig_H)

         # Get coating averages:

         # Thickness
         # [1] eqn. 53
         d_c = np.sum(d_L)
         d_l = np.sum(d_L[::2])
         d_h = np.sum(d_L[1::2])

         # Heat capacity
         # [1] eqn. 54
         c_c= (C_L * d_l + C_H * d_h) / d_c

         # Thermal conductivity
         # [1] eqn. 55
         kc = d_c / ((1 / K_L) * d_l + (1 / K_H) * d_h)

         # Effective substrate thermal expansion
         a_s = 2 * alp_s * (1 + sig_s) * c_c/ C_s

         # Get coating reflectivity:
         # [1] appendix B
         # Refractive indices
         n_all = np.vstack((1, n_l, n_s))

         # Reflectivities at interfaces
         # [1] eqn. 56
         r = (n_all[:-1] - n_all[1:]) / (n_all[:-1] + n_all[1:])

         # [1] eqn. 58
         rbar = np.zeros(r.shape, dtype=complex)
         ephi = np.zeros(r.shape, dtype=complex)
         ephi[-1] = np.exp(-4j * np.pi * d[-1])
         rbar[-1] = ephi[-1] * r[-1]

         for n in range(len(d), 0, -1):
            # One-way phase in layer n
            # [1] eqn. 59
            if n > 1:
               ephi[n - 1] = np.exp(-4j * np.pi * d[n - 2])
            else:
               ephi[n - 1] = 1

            # Accumulate reflecitivity
            # [1] eqn. 58
            rbar[n - 1] = ephi[n - 1] * (r[n - 1] + rbar[n]) / (
               1 + r[n - 1] * rbar[n])

         # Reflectivity derivatives
         # [1] eqn. 60
         dr_dphi = np.zeros(d.shape, dtype=complex)

         for n in range(len(d), 0, -1):
            dr_dphi[n - 1] = -1j * rbar[n]

            for m in range(n, 0, -1):
               dr_dphi[n-1] = dr_dphi[n-1]*ephi[m-1]*(1 - pow(r[m-1], 2))/\
                    pow(1 + r[m-1] * rbar[m], 2)

         # Rewriting geometrical thickness without lambda
         d_geo = d / n_l

         # Phase derivatives
         # [1] eqn. 61, 62, 63
         dphi_dd = 4 * np.pi * np.imag(dr_dphi / rbar[0])
         # Thermo-refractive
         dphi_TR = np.sum(dphi_dd * (bL + sL * n_l) * d_geo)
         # Thermo-elastic
         dphi_TE = 4 * np.pi * np.sum(aL * d_geo)
         # Total
         dphi_dT = dphi_TR + dphi_TE
         # Coating reflectivity
         r_c = rbar[0]

         # Calculate finite sized mass correction
         z = jn_zeros(1, 300)

         # Specific heat
         c_r = c_c/ C_s

         # Coating average value:
         # X = alpha*(1 + sigma)/(1 - sigma)
         x_l = alp_L * (1 + sig_L) / (1 - sig_L)
         x_h = alp_H * (1 + sig_H) / (1 - sig_H)
         XC = (x_l * d_l + x_h * d_h) / d_c
         XR = XC / alp_s

         # Coating average value:
         # Y = alpha*Y/(1 - sigma)
         y_l = alp_L * Y_L / (1 - sig_L)
         y_h = alp_H * Y_H / (1 - sig_H)
         Y_c = (y_l * d_l + y_h * d_h) / d_c
         Y_r = Y_c / (alp_s * Y_s)

         # Coating average value:
         # Z = 1/(1 + sigma)
         z_L = 1 / (1 - sig_L)
         z_H = 1 / (1 - sig_H)
         Z_c = (z_L * d_l + z_H * d_h) / d_c

         # The following is used in GWINC and references an unspecified
         # Braginskii paper, which I have yet to source, but will reference
         # with [2]. - IRS

         # Beam size parameter
         r_0 = wb / np.sqrt(2)

         # Values of J0 at zeroes of J1
         j_0m = jn(0, z)
         # [2] eqns. 77-78
         k_m = z / R_s
         Q_m = np.exp(-2 * k_m * H_s)
         p_m = np.exp(-pow(k_m * r_0 / 2, 2)) / j_0m

         # [2] eqn. 88
         c1 = 1 + sig_s
         c1m = 1 - sig_s
         c2 = pow(1 - Q_m, 2)
         c3 = pow(k_m * H_s, 2) * Q_m
         c4 = (1 - 2 * sig_s)
         L_m = XR - Z_c * c1 + (Y_r * c4 + Z_c - 2 * c_r) * c1 * c2 / (c2 - 4 * c3)

         # [2] eqns. 90 and 91
         s1 = (12 * pow(R_s / H_s, 2)) * np.sum(p_m / pow(z, 2))
         s2 = np.sum(pow(p_m * L_m, 2))
         P = pow(XR - 2 * sig_s * Y_r - c_r + s1 * (c_r - Y_r * c1m), 2) + s2

         # [2] eqns. 60 and 70
         Lambda = -c_r + (XR / c1 + Y_r * c4) / 2

         # [2] eqn. 92
         C_fsm = r_0 / (R_s * c1 * Lambda) * np.sqrt(P / 2)

         R = pow(abs(r_c), 2)
         T = 1 - R

         # Phase -> meters, subtracting substrate component
         dTR = dphi_TR * lam / (4 * np.pi)
         dTE = C_fsm * (dphi_TE * lam / (4 * np.pi) - a_s * d_c)

         # Sum thermoelastic and thermorefractive effects
         dTO = dTE + dTR

         # Get finite coating thickness correction
         # [1] section 3
         # [1] eqn. 39
         R_s = np.sqrt(c_c* kc / (C_s * K_s))
         x_i = d_c * np.sqrt(2 * w * c_c/ kc)

         # Trigonometric functions of x_i
         # [1] eqns. 43
         s = np.sin(x_i)
         c = np.cos(x_i)
         s2 = np.sin(x_i / 2)
         sh = np.sinh(x_i)
         ch = np.cosh(x_i)
         sh2 = np.sinh(x_i / 2)
         ch2 = np.cosh(x_i / 2)

         pR = dTR / (dTR + dTE)
         pE = dTE / (dTR + dTE)

         ap = 1 + pow(R_s, 2)
         am = 1 - pow(R_s, 2)

         # [1] eqns. 42
         g0 = 2 * (sh - s) + 2 * R_s * (ch - c)
         g1 = 8 * s2 * (R_s * ch2 + sh2)
         g2 = ap * sh + am * s + 2 * R_s * ch
         g3 = ap * ch + am * c + 2 * R_s * sh

         # [1] leading eqn. 42
         gTO = (pow(pE, 2)*g0 + pE*pR*x_i*g1 + g2*pow(pR*x_i, 2))/\
             (R_s*g3*pow(x_i, 2))

         # Thermal diffusion length
         # [1] eqn. 19
         r_tdl = np.sqrt(2 * K_s / (C_s * w))
         # [1] eqn. 26
         n_therm = 4 * kbT2 / (np.pi * w * C_s * r_tdl * pow(wb, 2))
         ntoZ = n_therm * gTO * pow(dTO, 2)

         return ntoZ

      n_titm = getNoise(w_itm, d_itm[:])
      n_tetm = getNoise(w_etm, d_etm[:])

      # Noise power spectral density
      n = 2 * (n_titm + n_tetm) / pow(L, 2)

      return np.sqrt(n)