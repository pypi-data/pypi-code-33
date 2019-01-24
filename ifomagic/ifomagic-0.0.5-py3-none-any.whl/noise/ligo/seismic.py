'''
Seismic noise class for aLIGO, in_herits from NoiseParent.

The default seismic noise curve represents the strain induced in the 
suspension and isolation components when seismic oscillations travel 
through these systems to the test masses.

References: 

MAGIC
@author: Isobel
'''
from copy import deepcopy
from scipy.interpolate import interp1d
from magic.noise import NoiseParent
import numpy as np


class SeismicNoise(NoiseParent):

    def getNoise(self):
        return self.seismic()

    def seismic(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency range
        f = params['frequency']
        # Horizontal suspension transfer function
        h_table = params['suspension_htable']
        # Vertical suspension transfer function
        v_table = params['suspension_vtable']
        # Vertical to beamline coupling angle
        theta = params['suspension_VH_coupling_theta']
        # Arm length
        L = params['length']
        # Number of stages
        n_stages = len(params['mirror_mass'])

        # Noise input
        # Frequencies
        seis_f = params['seismic_array_f']
        # Oscillations
        seis_x = params['seismic_array_x']
        # Interpolate to get exponent
        power = interp1d(seis_f, np.log10(seis_x), \
          bounds_error=False, fill_value=-14)(f)
        n_x = pow(10, power)

        # Horizontal noise
        n_h = pow(abs(h_table), 2) * pow(n_x, 2)
        # Vertical noise
        n_v = pow(abs(theta * v_table), 2) * pow(n_x, 2)

        # Noise power spectral density
        # 4 test masses
        n = n_stages * (n_v + n_h) / pow(L, 2)

        return np.sqrt(n)