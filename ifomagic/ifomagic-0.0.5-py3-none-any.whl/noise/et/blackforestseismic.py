'''
Seismic noise model for Einstein Telescope. Based on Jungle site seismic noise
in Space-Py Quest, which is an approximation of the Black Forest (quiet site)
noise.
We have taken out the use of a Q-factor, as this should be encompassed in other
detector parameters.

References:

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from magic import constants
from magic.utils.et import ground_motion
import numpy as np


class SeismicNoise(NoiseParent):

    def getNoise(self):
        return self.seismic()

    def seismic(self):

        # Get frequency
        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency range
        f = params['frequency']
        # Arm length
        L = params['length']
        # Suspension length
        l = params['suspension_length']
        # Number of suspension stages
        n_stages = len(l)
        # Get final suspension length
        l = l[0]

        # Get the ground motion
        X_seis = ground_motion.calculate(f)

        # Resonant frequency of pendulum
        f_pend = pow(constants.g / l, 0.5) / (np.pi * 2)
        # Pendulum motion to test mass motion
        tf = pow(1 + pow(f / f_pend, 4) - 2 * pow(f / f_pend, 2), -(n_stages))

        # Amplitude spectral density
        n = X_seis * 2 / L * tf

        return n