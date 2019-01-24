'''
Calculates the detector's power recycling factor.

References:

MAGIC
@author: Isobel
'''
from copy import deepcopy
import numpy as np


def calculate(ifo):

   # Assign parameters
   params = deepcopy(ifo.parameters)
   t_i = params['itm_transmittance']
   t_e = params['etm_transmittance']
   prmT = params['prm_transmittance']
   t_1 = np.sqrt(t_i)
   r_1 = np.sqrt(1 - t_i)
   t_2 = np.sqrt(t_e)
   r_2 = np.sqrt(1 - t_e)
   finesse = params['finesse']
   bs_loss = params['bs_loss']
   loss = params['optical_loss']


   r_arm = r_1 - pow(t_1, 2)*r_2*np.sqrt(1 - 2*loss)/\
                 (1 - r_1*r_2*np.sqrt(1 - 2*loss))

   t_5 = np.sqrt(prmT)
   r_5 = np.sqrt(1 - prmT)

   return pow(t_5, 2) / pow(1 + r_5 * r_arm * np.sqrt(1 - bs_loss), 2)