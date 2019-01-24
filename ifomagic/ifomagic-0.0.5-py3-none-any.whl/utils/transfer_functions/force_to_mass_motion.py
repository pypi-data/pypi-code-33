'''
Tranfer function from force on the test mass to its motion.
A is the equation of mortion matrix and B is the matrix of 
solutions to these equations.
k is an array of spring constants, and f is an array of 
frequencies.

References:

MAGIC
@author: Isobel
'''
import numpy as np


def calculate(A, B, f):

    X = np.zeros([B.size, A[0, 0, :].size], dtype=complex)

    for j in range(A[0, 0, :].size):
        X[:, j] = np.linalg.solve(A[:, :, j], B)

    # TF: Force on the TM -> TM motion
    h_force = np.zeros(f.shape, dtype=complex)
    h_force[:] = X[3, :]

    return h_force