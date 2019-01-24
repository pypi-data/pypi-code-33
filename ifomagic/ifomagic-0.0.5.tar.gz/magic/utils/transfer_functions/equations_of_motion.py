'''
Equations of motion for a pendulum.
k is an array of spring constants, m is an array of masses, and f is an 
array of frequencies.

References:

MAGIC
@author: Isobel
'''
import numpy as np


def calculate(k, m, f):

   # Angluar frequency
   w = 2 * np.pi * f
   # Solutions
   A = np.zeros((len(k), len(k), f.size), dtype=complex)

   for i in range(0, len(k) - 1):
      # Goes over range 0-2
      A[i, i + 1, :] = -k[i + 1, :]
      A[i + 1, i, :] = A[1, 2, :]
      A[i, i, :] = k[i, :] + k[i + 1, :] - m[i] * pow(w, 2)

   # Reset last stage
   A[-1, -2, :] = A[-2, -1, :]
   A[-1, -1, :] = k[-1, :] - m[-1] * pow(w, 2)

   return A