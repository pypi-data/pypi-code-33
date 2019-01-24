'''
Adding injection losses to a squeezed field.

References:

MAGIC
@author: Isobel
'''

import numpy as np


def calculate(m_in, L):

   minshape = m_in.shape
   eye = np.eye(minshape[0], minshape[1])
   M_eye = np.transpose(np.tile(eye, (minshape[2], 1, 1)), axes=(1, 2, 0))
   M_out = np.hstack((m_in * np.sqrt(1 - L), M_eye * np.sqrt(L)))

   return M_out