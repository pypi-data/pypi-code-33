'''
Class containing Einstein Telescope interferometer parameters.
This model is based on the premise that ET extends the existing design
for Voyager. All values are from reference [3] un_less otherwise specified.
References:
--- [1] Einstein Telescope Conceptual Design Study (2011)
   http://www.et-gw.eu/index.php/etdsdocument
--- [2] Freise, A et al 2009 Class. Quantum Grav. 26 085012
   https://arxiv.org/pdf/0804.1036.pdf
--- [3] Direct communication with Andreas Freise

MAGIC
@author: Isobel
'''
import numpy as np
from magic.detectors import Voyager
from magic.noise.et import SeismicNoise
from magic.noise.et import NewtonianNoise

from copy import deepcopy

# CLASS UNDER CONSTRUCTION < NOT STABLE


class ET(Voyager):

    # Initialisation
    def __init__(self,
                 f=None,
                 xlim=None,
                 ylim=None,
                 parameters={},
                 verbose=False):

        f = np.logspace(0, 4, 250)
        ylim = [3E-26, 4E-21]
        xlim = [1E0, 3E3]

        Voyager.__init__(
            self,
            f=f,
            xlim=xlim,
            ylim=ylim,
            parameters=parameters,
            verbose=verbose)

    # Treat as private
    # Initialise paramaters
    def _initialise_parameters(self, parameters={}):

        Voyager._initialise_parameters(self)

        # Basics
        self.parameters['power'] = 250  # W
        self.parameters['length'] = 10000  # m

        # Mass
        self.parameters['mirror_mass'][0] = 211  # kg
        # [1]
        # Could be 0.2 for low-frequency
        # Could be 0.3 for high-frequency
        self.parameters['mass_radius'] = 0.3  # m

        # Susupension
        self.parameters['suspension_length'][0] = 1.5  # m
        # IRS TODO just noticed temperature array is opposite config to others,
        # where first element is final stage
        self.parameters['suspension_temperature'][-1] = 120  # K
        self.parameters['substrate_temperature'] = 120  # K
        self.parameters['suspension_fiber_type'] = 'round'
        self.parameters['fiber_radius'] = 1.5E-3  # m

        # Recalculate temperature dependent material parameters
        T = self.parameters['suspension_temperature'][-1]
        new_dlnE_dT = self.parameters['materials']['suspension'][
            'silicon'].calcNewdlnEdT(T)
        new_alpha = self.parameters['materials']['suspension'][
            'silicon'].calcNewAlpha(T)
        new_dict = {'dlnE_dT': new_dlnE_dT, 'alpha': new_alpha}
        self.parameters['suspension_fiber_material'].updateProperties(new_dict)
        new_C = self.parameters['materials']['mirror']['silicon'].calcNewCm(
            self.parameters['substrate_temperature'])
        newer_dict = {'C': new_C}
        self.parameters['substrate_material'].updateProperties(newer_dict)

        # Seismic

        # Mirror
        '''
      self.parameters['itm_transmittance'] \
       = self.parameters['itm_transmittance'] / 4
      '''
        # From [1]
        # self.parameters['itm_transmittance'] = 0.007
        '''
      self.parameters['etm_transmittance'] = 6E-6
      self.parameters['output_filter_cavity_round_trip_loss'] = 75E-6
      self.parameters['prm_transmittance'] = 0.046
      '''
        self.parameters['itm_curvature'] = 5580  # m
        self.parameters['etm_curvature'] = 5580  # m

        # Residual gas
        # [1]: ET requires a base pressure below 1E-10 mbar (1E-7 Pa)
        # Not including right now as different to plot
        # self.parameters['residual_gas_pressure'] = 1E-7  # Pa

        # Coating

        # Optics and power
        self.parameters['pd_efficiency'] = 0.98

        # Location

        # Squeezer
        self.parameters[
            'output_filter_cavity_T_im'] = self.parameters['squeezer_filter_cavity_T_im'] / 4
        self.parameters['squeezer_squeeze_angle'] = 10 * np.pi / 180 # SQZ phase [radians]
        # Update settable parameter names
        self.variable_keys = deepcopy(list(self.parameters.keys()))

        Voyager._update_parameters(self, parameters)

    # Perform calculations
    def _performCalculations(self, parameters={}):

        Voyager._performCalculations(self, parameters)

    # Set ET-specific noise models
    def _set_noise_models(self, noise_models={}):

        Voyager._set_noise_models(self, noise_models)

        self.noise_models['Seismic'] = SeismicNoise(self)
        self.noise_models['Newtonian'] = NewtonianNoise(self)