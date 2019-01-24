'''
Ground motion, based on that at Jungle site in Space-Py Quest, which is 
an approximation of the Black Forest ground motion.

References:

MAGIC
@author: Isobel
'''
import numpy as np


def calculate(f):
   # Set up parameters as defined in Space-Py Quest
   X_dc = 200
   f_c = 0.02
   n_0 = 4
   X_hf = 5E-14

   # Get ground noise
   X_0 = X_dc / (1 + pow(f / f_c, n_0)) + X_hf
   # Allow some scaling, used to tune to correct magnitude.
   # Represents the noise reduction due to depth in SPQ.
   d = 1000
   dig = 1 / np.sqrt(1 + pow(d / 50, 4)) 

   # Get the reduced ground noise
   X_seis = X_0 * dig

   return X_seis