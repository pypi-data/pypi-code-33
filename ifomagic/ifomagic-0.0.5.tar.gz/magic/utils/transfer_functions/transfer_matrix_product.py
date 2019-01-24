'''
Get the product of two transfer matrices.

References:

MAGIC
@author: Isobel
'''

import numpy as np

def calculate(LHS, RHS):

   N = LHS.shape[0]
   M = RHS.shape[1]

   if len(LHS.shape) < 3 or LHS.shape[2] == 1:
      n_freq = RHS.shape[2]
      product = np.zeros((N, M, n_freq), dtype=complex)
      for n in range(n_freq):
         product[:, :, n] = np.dot(np.squeeze(LHS), RHS[:, :, n])
   elif len(RHS.shape) < 3 or RHS.shape[2] == 1:
      n_freq = LHS.shape[2]
      product = np.zeros((N, M, n_freq), dtype=complex)
      for n in range(n_freq):
         product[:, :, n] = np.dot(LHS[:, :, n], np.squeeze(RHS))
   elif LHS.shape[2] == RHS.shape[2]:
      n_freq = LHS.shape[2]
      product = np.zeros((N, M, n_freq), dtype=complex)
      for n in range(n_freq):
         product[:, :, n] = np.dot(LHS[:, :, n], RHS[:, :, n])
   else:
      print('LHS shape:')
      print(LHS.shape)
      print('RHS shape:')
      print(RHS.shape)
      raise Exception('Matrix size discrepancy between LHS and RHS.')

   return product