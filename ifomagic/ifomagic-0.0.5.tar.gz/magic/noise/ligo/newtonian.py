'''
Newtonian gravity gradient noise class for aLIGO, in_herits from NoiseParent.

References:
--- [1] Hughes and Thorne 1998 Phys.Rev.D 58 122002
   https://arxiv.org/pdf/gr-qc/9806018.pdf
--- [2] Saulson 1984 Phys.Rev. D 30 
   http://dx.doi.org/10.1103/PhysRevD.30 732
--- [3] Driggers and Harms 2011 
   https://dcc.ligo.org/cgi-bin/private/DocDB/ShowDocument?docid=60064
--- [4] Waldman and Fritschel
   https://dcc.ligo.org/cgi-bin/private/DocDB/ShowDocument?docid=3315

MAGIC
@author: Isobel
'''
from copy import deepcopy
from magic.noise import NoiseParent
from magic import constants
import numpy as np


class NewtonianNoise(NoiseParent):

    def getNoise(self):
        return self.newtonian()

    def newtonian(self):

        # Assign parameters
        params = deepcopy(self.ifo.parameters)
        # Frequency range
        f = params['frequency']
        # Arm length
        L = params['length']
        # Local ground density
        rho = params['seismic_rho']
        # Factor to account for correlation between masses and mirror's
        # offset from ground level
        bet = params['seismic_beta']
        # Frequency at which 'flat' noise rolls off
        fk = params['seismic_knee_frequency']
        # Seismic noise level at f < fk
        a_1 = params['seismic_low_frequency_level']
        # Abruptness of change at fk
        gam = params['seismic_gamma']

        # Assign constants
        # Newton's gravitational constant
        G = constants.G

        # Theta-esque function, Fermi distribution
        # IRS TODO - raises a runtime warning of overflow in power. Also present in GWINC.
        with np.errstate(over='ignore'):
             coeff = pow(1 + pow(3, gam * (f - fk)), -1)

        # Ground noise modelisation location choice:
        if 'location' in params:
            if params['location'] == 'Hanford' :
                if self.verbose:
                    print(
                        'Newtonian gravity ground noise model based on LIGO Hanford'
                    )

                ground = pow(2 * np.pi * f, 1 / 3) * (
                    a_1 * coeff + a_1 * (1 - coeff) * pow(fk / f, 3))

            elif params['location'] == 'Livingston' :
                if self.verbose:
                    print(
                        'Newtonian gravity ground noise model based on LIGO Livingston'
                    )

                ground = 100 * (a_1 * coeff + a_1 *
                                (1 - coeff) * pow(fk / f, 2))

            else:
                if self.verbose:
                    print('Unrecognised location')
                ground = 0
        else:
            if self.verbose:
                print('No location set')
            ground = 0

        # Effective gravity gradient spring frequency
        f_gg = np.sqrt(G * rho) / (2 * np.pi)

        # Noise power spectral density
        n = pow((bet * 4 * np.pi / L) * pow(f_gg / f, 2) * ground, 2)

        n = n / pow(params['seismic_omicron'], 2)

        return np.sqrt(n)