'''
Class to calculate the noise curves at the detector.

Additional calculations include:

--- Detection range estimation, using either inspiral or full IMR signal 
  from merging binary systems to dictate SNR

References:
--- [1] Ajith et al 2009 Phys.Rev. D 79 129901 
  https://arxiv.org/abs/0710.2335

MAGIC
@author: Isobel and Roshni
'''

from copy import deepcopy
from magic import constants
import numpy as np
import scipy.integrate as integrate
from magic.tools import imr


class Calculator:

    def __init__(self, ifo):
        self.ifo = ifo
        self.curves = 0
        self.f = deepcopy(self.ifo.parameters['frequency'])

    def get_noise_curves(self, parameters=None):
        if parameters is None:
            parameters = {}

        self.ifo.reset_noise(parameters=parameters)

        curves = self.ifo.get_noise_curves()
        self.curves = curves

        return curves

    def calculateDetectorRange(self, m1, m2, full):

        # Conversions to natural units
        Mpc_nu = constants.Distances['MPC'] / constants.c
        M_sun_nu = constants.M_sun * constants.G / pow(constants.c, 3)

        # Assume snr threshold of 8
        snr = 8

        f0 = self.f[0]

        if self.curves == 0:
            S = self.get_noise_curves()["Total"]
        else:
            S = self.curves["Total"]
        # Get chirp mass
        mu = M_sun_nu * pow(m1 * m2, 3 / 5) / pow(m1 + m2, 1 / 5)

        # Get extended chirp mass
        Mu = 80 * pow(mu, 5 / 3) / (96 * pow(np.pi, 4 / 3) * pow(snr, 2))

        freqs = []

        if not full:
            # Get innermost Keplarian orbital frequency, where the sensitivity
            # line integral will end
            f_isco = 1 / (pow(6, 1.5) * np.pi * (m1 + m2) * M_sun_nu)
            # Get length of sensitivity curve between bounds
            length = []
            for fi, freq in enumerate(S.f):
                if f0 <= freq and freq <= f_isco:
                    length.append(S.asd[fi])
                    freqs.append(freq)
            # Actual signal
            P = [
                pow(freqs[i], -7 / 6) * np.sqrt(Mu) / Mpc_nu / 2.26
                for i in range(len(freqs))
            ]
            # Get sensitivity function to go inside integral
            F = [
                Mu * pow(freqs[i], -7 / 3) / pow(length[i], 2)
                for i in range(len(freqs))
            ]
            I = integrate.simps(F, freqs)
            # Find detector distance
            D = np.sqrt(I) / Mpc_nu / 2.26

        else:
            # Based on IMRPhenomB model by Ajith et el.
            # Set source parameters using masses
            source = imr.setSource(m1, m2)
            # Values used in distance calculation
            symmetric_mass = source['symmetric_mass']
            total_mass = source['total_mass']
            f_merge = source['f_merge']
            # convert to Hz
            f_cutoff = source['f_cutoff'] * constants.c
            length = []
            for fi, freq in enumerate(S.f):
                if f0 <= freq and freq <= f_cutoff:
                    length.append(S.asd[fi])
                    freqs.append(freq)

            F = [
                pow(imr.IMRPhenomBModel(source, freqs[i]), 2) /
                pow(length[i], 2) for i in range(len(freqs))
            ]
            # Calculate integral in App B3.
            I = integrate.simps(F, freqs)
            # Distance calculation following[1]
            # Constant containing all components of Appendix B3 except frequency,
            # where the equation has been solved for d_l
            distance_constant = pow(f_merge, -7.0/6.0)*pow(total_mass, 5.0/6.0)\
                 *pow(5.0*symmetric_mass/6, 1.0/2.0)\
                     /(snr*pow(np.pi, 2.0/3.0))

            # The actual signal
            P = [
            distance_constant / constants.Distances['MPC'] * imr.IMRPhenomBModel(
            source, freqs[i]) / np.sqrt(freqs[i])
            for i in range(len(freqs))
            ]

            # Combining the terms and converting the result into physical units.
            D = np.sqrt(I) * distance_constant / constants.Distances['MPC']
        return D

    def calcInputSignalRange(self, strain, distance):
        # Source used is NSNS at 100Mpc, therefore use SNR~1/D scaling and
        # threshold of 8 to calculate distance at which source can be detected
        snr_threshold = 8
        snr = 2 * np.sqrt(self.calcSensitivityIntegral(strain, self.f))
        D = snr * distance / snr_threshold
        return D

    def calcSensitivityIntegral(self, strain, freq):
        # PSD
        _, S = self.get_noise_curves()["Total"]
        S = S**2
        # h^2/PSD
        y = pow(strain, 2) / S
        # Integrate to obtain SNR^2
        I = integrate.simps(y, freq)
        return I
