'''
Calculates the detector finesse.

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
    loss = params['optical_loss']

    return 2 * np.pi / (pow(T_itm, 2) + 2 * loss)
