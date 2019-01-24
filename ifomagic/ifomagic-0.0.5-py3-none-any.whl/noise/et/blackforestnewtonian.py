'''
Newtonian gravity gradient noise model for Einstein Telescope. Based on 
Jungle site newtonian noise in Space-Py Quest, which is an approximation of 
the Black Forest (quiet site) noise.

References:

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from magic.utils.et import ground_motion


class NewtonianNoise(NoiseParent):

    def getNoise(self):
        return self.newtonian()

    def newtonian(self):

        # Get frequency
        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency range
        f = params['frequency']
        # Arm length
        L = params['length']

        # Get the ground motion
        X_seis = ground_motion.calculate(f)

        # Amplitude spectral density
        n = X_seis * 2.4E-10 / L / pow(f, 1 / 2)

        return n