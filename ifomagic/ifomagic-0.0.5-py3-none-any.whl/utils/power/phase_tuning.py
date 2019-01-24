'''
Calculating the phase gain in the signal recycling cavity.

References:

MAGIC
@author: Isobel
'''
from copy import deepcopy
from math import fmod
from magic import constants
import numpy as np
from scipy.optimize import minimize_scalar


def calculate(ifo):

   # Assign parameters
   params = deepcopy(ifo.parameters)
   # Wavelength
   w_0 = params['laser_carrier_frequency']
   # Signal recycling cavity length
   l = params['src_length']

   # Phase tuning
   phi = w_0 * l / constants.c

   # Modulo 2 * pi
   phi = fmod(phi, 2 * np.pi)

   return phi