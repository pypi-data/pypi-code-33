'''
Calculates the power at the beam splitter.

References:

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic import constants


def calculate(ifo):
   # Get ifo beamsplitter power, arm power, power recycling factor,
   # and mirror transmission
   # Assign parameters
   params = deepcopy(ifo.parameters)
   P = params['power']
   prfactor = params['power_recycling_factor']

   return P * prfactor
