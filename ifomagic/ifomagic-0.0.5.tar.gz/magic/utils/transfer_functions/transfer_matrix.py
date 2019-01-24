'''
Make a transfer matrix. 

References:

MAGIC
@author: Isobel
'''

import numpy as np

def calculate(A11, A12, A21, A22):
   # Create a transfer matrix

   n_functions = np.max(
      [np.size(A11), np.size(A12),
       np.size(A21), np.size(A22)])
   # Pad out with 1s
   if np.size(A11) == 1:
      A11 = A11 * np.ones(n_functions)
   if np.size(A12) == 1:
      A12 = A12 * np.ones(n_functions)
   if np.size(A21) == 1:
      A21 = A21 * np.ones(n_functions)
   if np.size(A22) == 1:
      A22 = A22 * np.ones(n_functions)

   M = np.zeros((2, 2, n_functions), dtype=complex)
   for func in range(n_functions):
      M[:, :, func] = np.array([[A11[func], A12[func]], [A21[func],
                                                         A22[func]]])

   return M