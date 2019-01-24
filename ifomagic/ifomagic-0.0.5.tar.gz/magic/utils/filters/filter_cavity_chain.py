'''
Provide the reflection matrix for vacuum fluctuations entering the input 
mirror, and the transmission matrix for vacuum fluctuations entering the 
end mirror, of a chain of filter cavities. 

References:

MAGIC
@author: Isobel
'''
from magic.utils.filters import filter_cavity
import magic.utils.transfer_functions.transfer_matrix as transfer_matrix
import magic.utils.transfer_functions.transfer_matrix_product as transfer_matrix_product
import numpy as np


def calculate(f, p, M_n):

    # Identity matrix
    I = transfer_matrix.calculate(np.ones(f.shape), 0, 0, 1)

    # Filter cavity chain transfer relation
    rot = p['rot']

    M_R, M_T, M_noise = filter_cavity.calculate(f, p, rot, M_n)

    # Apply post-filter cavity rotation
    cr = np.cos(rot)
    sr = np.sin(rot)
    M_rot = np.array([[cr, -sr], [sr, cr]])

    M_noise = transfer_matrix_product.calculate(M_rot, M_noise)

    # Update M_transfer
    I_M_R = transfer_matrix_product.calculate(M_R, I)
    M_transfer = transfer_matrix_product.calculate(M_rot, I_M_R)

    return M_transfer, M_noise
