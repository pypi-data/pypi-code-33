'''
Tranfer function from table motion to test mass motion.
A is the equation of mortion matrix and B is the matrix of 
solutions to these equations.
k is an array of spring constants, and f is an array of 
frequencies.

References:

MAGIC
@author: Isobel
'''
import numpy as np


def calculate(A, B, k, f):

   X = np.zeros([B.size, A[0, 0, :].size], dtype=complex)

   for j in range(A[0, 0, :].size):
      X[:, j] = np.linalg.solve(A[:, :, j], B)

   # TF: Table motion -> TM motion
   table = np.zeros(f.shape, dtype=complex)
   table[:] = X[0, :]
   table = table * k[0, :]

   return table