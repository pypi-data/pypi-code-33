'''
Calculates the power in the interferometer arms.

References:

MAGIC
@author: Isobel
'''
from copy import deepcopy
import numpy as np


def calculate(ifo):

   # Assign parameters
   params = deepcopy(ifo.parameters)

   T_itm = np.sqrt(params['itm_transmittance'])
   R_itm = np.sqrt(1 - params['itm_transmittance'])
   R_etm = np.sqrt(1 - params['etm_transmittance'])
   bs_power = params['bs_power']

   loss = params['optical_loss']

   gain_arm = T_itm / (1 - R_itm * R_etm * np.sqrt(1 - 2 * loss))

   return bs_power * pow(gain_arm, 2) / 2
