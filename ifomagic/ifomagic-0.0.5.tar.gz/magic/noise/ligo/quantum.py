'''
Quantum noise class, in_herits from NoiseParent.

References:
--- [1] Buonanno and Chen 2001 Phys.Rev. D 64 042006
   https://journals.aps.org/prd/abstract/10.1103/PhysRevD.64.042006
--- [2] Kimble et al. 2001 Phys.Rev. D 65 022002
   https://journals.aps.org/prd/pdf/10.1103/PhysRevD.65.022002
--- [3] Buonanno and Chen 2004 Phys.Rev. D 69 102004
   https://journals.aps.org/prd/abstract/10.1103/PhysRevD.69.102004

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from magic import constants
import numpy as np

from magic.utils.filters import injection_loss
from magic.utils.filters import filter_cavity_chain
from magic.utils.filters import signal_recycling

from magic.utils.transfer_functions import transfer_matrix
from magic.utils.transfer_functions import transfer_matrix_product

class QuantumNoise(NoiseParent):

    def getNoise(self):
        return self.quantum()

    def quantum(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency range
        f = params['frequency']

        # Filter cavity chain effects (boolean)
        apply_frequency_dependent_squeezing = params[
            'frequency_dependent_squeezing']

        coeff, M_ifo, M_signal, M_noise = signal_recycling.calculate(params)

        # Get squeezer information
        if params['squeezer_type'] == 'none' :
            squeeze_db = 0
            alpha = 0
            loss_in = 0
            anti_squeeze_db = 0
        else:
            squeeze_db = params['squeezer_amplitude_db']
            alpha = params['squeezer_squeeze_angle']
            loss_in = params['squeezer_injection_loss']
            anti_squeeze_db = -squeeze_db

        # Input squeezing matrix
        R = squeeze_db / (20 * np.log10(np.exp(1)))
        anti_R = anti_squeeze_db / (20 * np.log10(np.exp(1)))
        M_squeeze = np.array([[np.exp(-R), 0], [0, np.exp(anti_R)]])

        M_squeeze = np.transpose(
            np.tile(M_squeeze, (len(f), 1, 1)), axes=(1, 2, 0))


        # Adding input rotation
        sa = np.sin(alpha)
        ca = np.cos(alpha)
        M_rotate = transfer_matrix.calculate(ca, -sa, sa, ca)
        M_squeeze = transfer_matrix_product.calculate(M_rotate, M_squeeze)
        # Include losses
        M_squeeze = injection_loss.calculate(M_squeeze, loss_in)

        if apply_frequency_dependent_squeezing:
            squeezer = {
                'L_f' :
                params['squeezer_filter_cavity_l'],
                'f_detune' :
                params['squeezer_filter_cavity_f_detune'],
                'T_im' :
                params['squeezer_filter_cavity_T_im'],
                'T_em' :
                params['squeezer_filter_cavity_T_em'],
                'round_trip_loss' :
                params['squeezer_filter_cavity_round_trip_loss'],
                'rot' :
                params['squeezer_filter_cavity_rot']
            }
            M_rotate, M_squeeze = filter_cavity_chain.calculate(
                f, squeezer, M_squeeze)

        # Get total quantum noise
        M_squeeze = transfer_matrix_product.calculate(M_ifo, M_squeeze)
        M_noise = np.hstack((M_squeeze, M_noise))

        loss_pd = 1 - params['pd_efficiency']
        eta = params['quad_readoutput_phase']
        M_noise = injection_loss.calculate(M_noise, loss_pd)
        M_signal = M_signal * np.sqrt(1 - loss_pd)
        M_readout = np.array([[np.sin(eta), np.cos(eta)]])

        n_a = pow(abs(transfer_matrix_product.calculate(M_readout, M_noise)), 2)
        n_a = np.squeeze(np.sum(n_a, axis=1))
        n_b = pow(abs(transfer_matrix_product.calculate(M_readout, M_signal)), 2)
        n_b = np.squeeze(np.sum(n_b, axis=1))

        # Noise power spectral density
        n = coeff * n_a / n_b

        return np.sqrt(n)