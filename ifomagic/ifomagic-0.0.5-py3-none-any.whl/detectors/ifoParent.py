'''
Parent class for interferometer models.

MAGIC
@author: Isobel
'''
import abc

import numpy as np

from magic import constants
from magic.constants import UNSET
# Noise classes
from magic.noise.ligo import SeismicNoise
from magic.noise.ligo import CoatingBrownianNoise
from magic.noise.ligo import CoatingThermoOpticNoise
from magic.noise.ligo import SubstrateBrownianNoise
from magic.noise.ligo import SubstrateThermoElasticNoise
from magic.noise.ligo import SuspensionThermalNoise
from magic.noise.ligo import ResidualGasNoise
from magic.noise.ligo import NewtonianNoise
from magic.noise.ligo import QuantumNoise
# Optics utils
from magic.utils.optics import optical_thickness
# Power utils
from magic.utils.power import finesse
from magic.utils.power import power_recycling_factor
from magic.utils.power import bs_power
from magic.utils.power import arm_power
from magic.utils.power import beam_size
from magic.utils.power import phase_tuning
# Mirror
import magic.materials.mirror.silica as mirror_silica
import magic.materials.mirror.silicon as mirror_silicon
# Suspension
import magic.materials.suspension.silica as suspension_silica
import magic.materials.suspension.c70steel as suspension_c70steel
import magic.materials.suspension.silicon as suspension_silicon
import magic.materials.suspension.marsteel as suspension_marsteel
# Parameter tracking
import magic.tools.parameter_tracking as parameter_tracking

from magic.curve import Curve


class NoiseNotImplementedError(Exception):
    """
    Raised when a given noise model is not implemented for the detector
    """

    def __init__(self, ifo_name, noise_model):
        self.ifo_name = ifo_name
        self.noise_model = noise_model
        self.message = "noise model {} not implemented for ifo {}".format(ifo_name, noise_model)


class IfoParent(object):
    """
    Base class from which all interferometers are derived
    """

    __metaclass__ = abc.ABCMeta

    # Initialisation
    @abc.abstractmethod
    def __init__(self,
                 f,
                 xlim,
                 ylim,
                 parameters={},
                 verbose=False,
                 kat_file=None):

        self.f = f
        self.verbose = verbose
        self.kat_file = kat_file

        self.constants = constants
        self.parameters = {}
        self.noise_models = {}
        self.plotting = {}
        self.utils = {}
        self.tools = {}

        # Set up plotting specifications
        self.plotting['ylim'] = ylim
        self.plotting['xlim'] = xlim

        # Set up utility functions to pass to children
        self.utils['optical_thickness'] = optical_thickness
        self.utils['finesse'] = finesse
        self.utils['power_recycling_factor'] = power_recycling_factor
        self.utils['bs_power'] = bs_power
        self.utils['arm_power'] = arm_power
        self.utils['beam_size'] = beam_size
        self.utils['phase_tuning'] = phase_tuning

        # Set up tools to pass to children
        self.tools['parameter_tracking'] = parameter_tracking

        self._initialise_parameters(parameters)

    # Public
    @abc.abstractmethod
    def reset_noise(self, noise_models=None, parameters=None):
        """
        Overwrite interferometer parameters with those given, calculating derived parameters, and then
        reset noise models using new parameters, finally overwriting noise models with those
        given in parameter
        :param noise_models: dictionary of noise models to add to/overwrite default ones with
        :param parameters: dictionary of parameters to add to/overwrite default ones with
        """
        if noise_models is None:
            noise_models = {}
        if parameters is None:
            parameters = {}

        if len(parameters) > 0:
            self._update_parameters(parameters=parameters)

        self._set_noise_models(noise_models=noise_models)

    def update_noise(self, noise_models):
        """
        Overwrite noise models with those given as parameter
        :param noise_models: To overwrite with
        """
        for key in noise_models:
            self.noise_models[key] = noise_models[key]

    def calculate_total_noise(self):
        """
        Calculate total ASD for detector
        Initializes noise models if needed
        :return: np array representing total _amplitude_ spectral density
        """

        self._init_noise_models_if_needed()

        total = 0

        for key, model in self.noise_models.items():
            total += np.power(model.getNoise(), 2)

        return np.sqrt(total)

    def get_noise(self, noise_model):
        """
        Get amplitude spectral density of noise model for this detector, raising NoiseNotImplementedError
        if the noise is not implemented for this detector.
        Initializes noise models if needed
        Returns total noise if noise_model == "Total"
        :param noise_model: noise model to get
        :return: np array representing _amplitude_ spectral density
        """

        if noise_model == "Total":
            return self.calculate_total_noise()

        self._init_noise_models_if_needed()

        if noise_model not in self.noise_models:
            raise NoiseNotImplementedError(self.__class__.__name__, noise_model)
        return self.noise_models[noise_model].getNoise()

    def get_noise_and_freq(self, noise_model):
        """
        Same as get_noise but also returns the frequency range
        :param noise_model: noise model to get
        :return Curve object
        """

        asd = self.get_noise(noise_model)
        assert len(self.f) == len(asd)
        return Curve(self.f, asd)

    def get_noise_models(self):
        """
        Return a list of names of noise models supported by interferometer
        :return: list of noise models
        """
        return self.noise_models.keys()

    def get_noise_curves(self):
        """
        Return a dictionary of all the noise curves, each one is a Curve object
        Initializes noise models if needed
        :return: dictionary with keys as noise models and values as curves
        """

        self._init_noise_models_if_needed()

        curves = {}

        for key in self.noise_models:
            curves[key] = self.get_noise_and_freq(key)

        curves["Total"] = self.get_noise_and_freq("Total")

        return curves

    # Treat as private
    # Initialise parameters
    @abc.abstractmethod
    def _initialise_parameters(self, parameters={}):

        if self.verbose:
            print(self.__class__.__name__ + ' initialising')

        # Settable parameter names
        self.variable_keys = [
            'file_path',
            'frequency',
            'temperature',
            'length',
            'wavelength',
            # Test mass macros
            'mirror_mass',
            'mass_radius',
            'mass_thickness',
            # Suspension
            'suspension_fiber_material',
            'suspension_fiber_type',
            'suspension_dilution',
            'suspension_k',
            'suspension_wire_rad',
            'suspension_blade_thickness',
            'suspension_Nwires',
            'suspension_length',
            'suspension_temperature',
            'suspension_fiber_type',
            # Seismic
            'seismic_knee_frequency',
            'seismic_low_frequency_level',
            'seismic_gamma',
            'seismic_rho',
            'seismic_beta',
            # Mirror
            'itm_transmittance',
            'etm_transmittance',
            'srm_transmittance',
            'prm_transmittance',
            'itm_curvature',
            'etm_curvature',
            'itm_coating_lown_thickness',
            'etm_coating_lown_thickness',
            'itm_coating_max_thickness',
            'etm_coating_max_thickness',
            # Residual gas
            'residual_gas_pressure',
            'residual_gas_mass',
            'residual_gas_polarizability',
            # Substrate
            'substrate_temperature',
            # Coating
            'coating_absorption',
            # High-n
            'coating_highn_Y',
            'coating_highn_index',
            'coating_highn_phi',
            'coating_highn_sigma',
            'coating_highn_alpha',
            'coating_highn_beta',
            'coating_highn_CV',
            'coating_highn_thermal_conductivity',
            # Low-n
            'coating_lown_Y',
            'coating_lown_index',
            'coating_lown_phi',
            'coating_lown_sigma',
            'coating_lown_alpha',
            'coating_lown_beta',
            'coating_lown_CV',
            'coating_lown_thermal_conductivity',
            # Optics and power
            'power',
            'src_length',
            'bs_loss',
            'tcs_src_loss',
            'optical_loss',
            'optical_coupling',
            'pd_efficiency',
            'p_crit',
            # Squeezer
            'squeezer_type',
            'squeezer_amplitude_db',
            'squeezer_injection_loss',
            'squeezer_squeeze_angle',
            'quad_readoutput_phase',
            # Output filter
            'output_filter_cavity_f_detune',
            'output_filter_cavity_l',
            'output_filter_cavity_T_im',
            'output_filter_cavity_T_em',
            'output_filter_cavity_round_trip_loss',
            'output_filter_cavity_rot'
        ]

        self.parameters = {k: UNSET for k in self.variable_keys}

        # Make all materials available to all children
        self.parameters['materials'] = {}
        self.parameters['materials']['suspension'] = {
            'silica' : suspension_silica.Silica(),
            'c70steel' : suspension_c70steel.C70Steel(),
            'marsteel' : suspension_marsteel.MaragingSteel(),
            'silicon' : suspension_silicon.Silicon()
        }

        self.parameters['materials']['mirror'] = {
            'silica' : mirror_silica.Silica(),
            'silicon' : mirror_silicon.Silicon()
        }

        self._update_parameters(parameters)

    # Set noise models
    @abc.abstractmethod
    def _set_noise_models(self, noise_models={}):

        self.noise_models['Seismic'] \
            = SeismicNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Coating Brownian'] \
            = CoatingBrownianNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Coating Thermo-Optic'] \
            = CoatingThermoOpticNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Substrate Brownian'] \
            = SubstrateBrownianNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Substrate Thermo-Elastic'] \
            = SubstrateThermoElasticNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Suspension Thermal'] \
            = SuspensionThermalNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Residual Gas'] \
            = ResidualGasNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Newtonian'] \
            = NewtonianNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Quantum'] \
            = QuantumNoise(ifo=self, verbose=self.verbose)

        # Add to or overwrite with any user-defined noise models
        self.update_noise(noise_models)

    # Update parameters
    def _update_parameters(self, parameters):

        # Add to or overwrite with any user-defined parameters
        if parameters:
            for key in parameters:
                self.parameters[key] = parameters[key]

    # Find where each of the detector's parameters are used
    def _getParameterUsage(self):

        path = './'
        pt = self.tools['parameter_tracking']
        np, nm, up, um = pt.findParameterUses(path, self.parameters)
        # Map noise name : parameters used
        self.noise_parameters = np
        # Map noise name : path to noise file
        self.noise_map = nm
        # Map utiliy name : parameters used
        self.utils_parameters = up
        # Map utility name : path to utility file
        self.utils_map = um

    # Condition to perform a calculation of a parameter
    def _conditionalCalculation(self, obj, param, parameters):

        # Unpack tool 
        pt = self.tools['parameter_tracking']
        dependencies = pt.searchForParameters(obj, self.parameters)
        evaluate = [d for d in dependencies if d in parameters.keys()]

        if (param not in self.parameters.keys() or len(evaluate) > 0) \
        and param not in parameters.keys():
            return True
        else:
            return False


    def _init_noise_models_if_needed(self):
        if len(self.noise_models) == 0:
            self.reset_noise()
