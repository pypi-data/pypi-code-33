'''
Class containing Cosmic Explorer Interferometer parameters

MAGIC
@author: Isobel
'''
import numpy as np
from magic.detectors import Voyager
from magic.noise.et import SeismicNoise
from magic.noise.et import NewtonianNoise
from magic import constants

from copy import deepcopy

# CLASS UNDER CONSTRUCTION < NOT STABLE


class CE(Voyager):

    # Set a default frequency range
    freq = np.logspace(0, 4, 250)
    # Set default plotting limits
    x_limits = [1E0, 3E3]
    y_limits = [3E-26, 4E-21]

    # Initialisation
    def __init__(self,
                 f=freq,
                 xlim=x_limits,
                 ylim=y_limits,
                 parameters={},
                 verbose=False):

        Voyager.__init__(
            self,
            f=f,
            xlim=xlim,
            ylim=ylim,
            parameters=parameters,
            verbose=verbose)

        self.plotting['ylim'] = ylim
        self.plotting['xlim'] = xlim

    # Treat as private
    # Initialise paramaters
    def _initialise_parameters(self, parameters={}):

        Voyager._initialise_parameters(self)

        self.parameters['length'] = 40000  # m
        self.parameters['mirror_mass'][0] = 320  # kg
        self.parameters['temperature'] = 123  # K
        self.parameters['suspension_temperature'][-1] = 120  # K

        # Update settable parameter names
        self.variable_keys = deepcopy(list(self.parameters.keys()))

        Voyager._update_parameters(self, parameters)