'''
Calculates beam radii and waist when using a Fabry-Perot cavity.

References:

MAGIC
@author: Isobel
'''
from copy import deepcopy
import numpy as np


def calculate(ifo):

   # Assign parameters
   params = deepcopy(ifo.parameters)
   L = params['length']
   g_itm = 1 - L / params['itm_curvature']
   g_etm = 1 - L / params['etm_curvature']
   lam = params['wavelength']

   # Beam size calculations
   # Prefactor
   pre = L * lam / np.pi
   # Common denominator
   denom = 1 - g_itm * g_etm

   # Beam size at ITM
   w_itm = pre * np.sqrt(abs(g_etm / g_itm / denom))
   w_itm = np.sqrt(w_itm)

   # Beam size at ETM
   w_etm = pre * np.sqrt(abs(g_itm / g_etm / denom))
   w_etm = np.sqrt(w_etm)

   # Beam size at waist
   w = g_itm * g_etm * denom
   w = pre * np.sqrt(abs(w / pow(g_itm + g_etm - 2 * g_itm * g_etm, 2)))
   w = np.sqrt(w)

   # Mirror position calculations
   post = L / (g_itm + g_etm - 2*g_itm*g_etm)
   # ITM position relative to waist
   z_itm = -g_etm * (1 - g_itm) * post
   # ETM position relative to waist
   z_etm = g_itm * (1 - g_etm) * post

   return w_itm, z_itm, w_etm, z_etm, w
