'''
Class containing aLIGO interferometer parameters, with some automatically 
in_herited from its parent IfoParent model, and most re-defined here.

TODO: Provide links to these 
References:
--- [1] LIGO-T000012-00-D

--- [2] Fejer et al

--- [3] Quartz Glass for Optics Data and Properties, Heraeus data sheet

--- [4] Gretarsson and Harry, Gretarsson thesis

MAGIC
@author: Isobel
'''

from magic.detectors import IfoParent
from magic.noise.ligo import SeismicNoise
from magic.noise.ligo import NewtonianNoise
from magic.noise.ligo import FinesseQuantumNoise
# Finesse quantum model appears to be working for aLIGO
from magic.utils.ligo import quad_transfer_functions
import numpy as np
from copy import deepcopy

class aLIGO(IfoParent):

    # Initialisation
    def __init__(self,
                 f=None,
                 xlim=None,
                 ylim=None,
                 parameters={},
                 verbose=False):

        IfoParent.__init__(
            self,
            f=f,
            xlim=xlim,
            ylim=ylim,
            parameters=parameters,
            verbose=verbose)

        # Set defaults that any children can use
        self.default_input = {
            'f': 5 * np.logspace(0, 3, 250),
            'ylim': [3E-25, 2.2E-22],
            'xlim': [5E0, 5E3],
        }

        self._check_or_set_defaults()

        # Add to utility functions
        self.utils['quad_transfer_functions'] = quad_transfer_functions

    # Public
    # Set up noise model
    def reset_noise(self, noise_models=None, parameters=None):
        if noise_models is None:
            noise_models = {}
        if parameters is None:
            parameters = {}

        if len(parameters) > 0:
            self._update_parameters(parameters=parameters)

        self._performCalculations(parameters=parameters)
        self._set_noise_models(noise_models=noise_models)

    # Treat as private
    # Initialise parameters
    def _initialise_parameters(self, parameters={}):

        IfoParent._initialise_parameters(self)

        self.parameters['frequency'] = self.f
        # No filter cavity chain
        self.parameters['frequency_dependent_squeezing'] = False
        # Basics
        self.parameters['temperature'] = 290  # K
        self.parameters['length'] = 3995  # m
        self.parameters['wavelength'] = 1.064E-6  # m
        # Mass
        self.parameters['mirror_mass'] = [39.6, 39.6, 21.8, 22.1]  # kg
        self.parameters['mass_radius'] = 0.17  # m
        self.parameters['mass_thickness'] = 0.2  # m
        # Suspension
        # Fiber material
        self.parameters['suspension_fiber_material'] \
        = self.parameters['materials']['suspension']['silica']
        # Round (silica) fibers
        self.parameters['suspension_fiber_type'] = 'round'
        self.parameters['suspension_dilution'] = [np.NaN, 106, 80, 87]
        self.parameters['suspension_k'] = [np.NaN, 5200, 3900,
                                           3400]  # vertical spring constant
        self.parameters['suspension_wire_rad'] = [
            np.NaN, 310E-6, 350E-6, 520E-6
        ]
        self.parameters['suspension_blade_thickness'] = [
            np.NaN, 4200E-6, 4600E-6, 4300E-6
        ]
        self.parameters['suspension_Nwires'] = [4, 4, 4, 2]
        self.parameters['suspension_length'] = [0.602, 0.341, 0.277,
                                                0.416]  # m
        self.parameters['suspension_temperature'] = [300, 300, 300, 300]  # K
        self.parameters['suspension_ribbon_width'] = 1150E-6  # m
        self.parameters['suspension_ribbon_thickness'] = 115E-6  # m
        self.parameters['fiber_radius'] = 205E-6  # m
        # Seismic
        self.parameters[
            'seismic_knee_frequency'] = 10  # Hz, freq where 'flat' noise rolls off
        self.parameters[
            'seismic_low_frequency_level'] = 1e-9  # m/rtHz, seismic noise level below f_knee
        self.parameters[
            'seismic_gamma'] = 0.8  # abruptness of change at f_knee
        self.parameters[
            'seismic_rho'] = 1.8e3  # kg/m^3, density of the ground nearby
        self.parameters['seismic_beta'] = 0.5
        # Actual arrays to interpolate
        self.parameters['seismic_array_f'] = np.array(
            [0.01, 0.03, 0.1, 0.2, 0.5, 1, 10, 30, 300])  # Hz
        self.parameters['seismic_array_x'] = np.array(
            [3e-6, 1e-6, 2e-7, 2e-7, 8e-10, 1e-11, 3e-13, 3e-14, 3e-14])  # m
        self.parameters[
            'seismic_omicron'] = 1  # Feedforward cancellation factor
        # Mirror
        self.parameters['itm_transmittance'] = 0.014  # transmittance of ITM
        self.parameters['etm_transmittance'] = 5E-6  # transmittance of ETM
        self.parameters['srm_transmittance'] = 0.20  # transmittance of SRM
        self.parameters['prm_transmittance'] = 0.03  # transmittance of PRM
        self.parameters['itm_curvature'] = 1970  # m
        self.parameters['etm_curvature'] = 2192  # m
        self.parameters['itm_coating_lown_thickness'] = 0.308
        self.parameters['etm_coating_lown_thickness'] = 0.27
        self.parameters['itm_coating_max_thickness'] = 0.5
        self.parameters['etm_coating_max_thickness'] = 0.5
        # Residual gas
        self.parameters['residual_gas_pressure'] = 4E-7  # Pa
        self.parameters['residual_gas_mass'] = 3.35E-27  # kg
        self.parameters['residual_gas_polarizability'] = 7.8E-31  # m^3
        # Substrate
        # Substrate material
        self.parameters['substrate_material'] \
        = self.parameters['materials']['mirror']['silica']

        self.parameters['substrate_temperature'] = 290  # K
        # Coating
        self.parameters['coating_absorption'] = 0.5E-6  # 1/m
        # High-n
        self.parameters['coating_highn_Y'] = 140E9
        self.parameters['coating_highn_index'] = 2.06539
        self.parameters['coating_highn_phi'] = 2.3E-4
        self.parameters['coating_highn_sigma'] = 0.23  # Poisson's ratio
        self.parameters[
            'coating_highn_alpha'] = 3.6E-6  # [2], zero crossing at 123 K
        self.parameters['coating_highn_beta'] = 1.4E-5  # dn/dT
        self.parameters[
            'coating_highn_CV'] = 2.1E6  # J/K/m^3 [2], volume-specific heat capacity
        self.parameters[
            'coating_highn_thermal_conductivity'] = 33  # J/m/s/K [2]
        # Low-n
        self.parameters['coating_lown_Y'] = 72E9
        self.parameters['coating_lown_index'] = 1.45
        self.parameters['coating_lown_phi'] = 4.0E-5
        self.parameters['coating_lown_sigma'] = 0.17  # Poisson's ratio
        self.parameters[
            'coating_lown_alpha'] = 5.1E-7  # [2], zero crossing at 123 K
        self.parameters['coating_lown_beta'] = 8E-6  # dn/dT
        self.parameters[
            'coating_lown_CV'] = 1.6412E6  # J/K/m^3 [2], volume-specific heat capacity
        self.parameters[
            'coating_lown_thermal_conductivity'] = 1.38  # J/m/s/K [2]
        # Optics and power
        self.parameters['power'] = 125  # W
        self.parameters['src_length'] = 55  # m, ITM to SRM distance
        self.parameters['bs_loss'] = 0.5E-3  # # power loss near beamsplitter
        self.parameters['tcs_src_loss'] = 0.0
        self.parameters[
            'optical_loss'] = 37.5E-6  # average per mirror power loss
        self.parameters['prc_loss'] = 5e-6/2
        self.parameters['optical_coupling'] = 1.0
        self.parameters[
            'pd_efficiency'] = 0.95  # photo-detector quantum efficiency
        self.parameters['p_crit'] = 10  # W, tolerable heating power
        self.parameters['src_phase_tuning'] = 0  # # SRM tuning [radians]
        # Squeezer
        self.parameters['squeezer_amplitude_db'] = 0  # SQZ amplitude [dB]
        self.parameters[
            'squeezer_injection_loss'] = 0.05  # power loss to squeeze
        self.parameters['squeezer_squeeze_angle'] = 0  # SQZ phase [radians]
        self.parameters[
            'quad_readoutput_phase'] = np.pi / 2  # # homoDyne phase [radians]
        self.parameters['squeezer_type'] = 'none'
        self.parameters['squeezer_filter_cavity_l'] = 30  # m, cavity length
        # Output filter
        self.parameters[
            'output_filter_cavity_f_detune'] = -14.5  # Hz, detuning
        self.parameters['output_filter_cavity_l'] = self.parameters[
            'length']  # m, cavity length
        self.parameters[
            'output_filter_cavity_T_im'] = 10E-3  # input mirror trasmission
        self.parameters[
            'output_filter_cavity_T_em'] = 0  # end mirror trasmission
        self.parameters[
            'output_filter_cavity_round_trip_loss'] = 100E-6  # round-trip loss in the cavity
        self.parameters[
            'output_filter_cavity_rot'] = 0  # phase rotation after cavity
        # Location
        self.parameters['location'] = 'Hanford'

        # Update settable parameter names
        self.variable_keys = deepcopy(list(self.parameters.keys()))

        IfoParent._update_parameters(self, parameters)

    # Check that no class variables are None
    def _check_or_set_defaults(self):

        if type(self.f) != np.ndarray:
            self.f = self.default_input['f']
            self.parameters['frequency'] = self.f
        if self.plotting['xlim'] == None:
            self.plotting['xlim'] = self.default_input['xlim']
        if self.plotting['ylim'] == None:
            self.plotting['ylim'] = self.default_input['ylim']

    # Perform calculations to determine derived parameters
    def _performCalculations(self, parameters={}):

        IfoParent._update_parameters(self, parameters)

        old_unsettables = [
            key for key in self.parameters.keys()
            if key not in self.variable_keys
        ]
        old_unsettables = {key: False for key in old_unsettables}

        # Unpack utility functions from self and parent
        fin = self.utils['finesse']
        prf = self.utils['power_recycling_factor']
        bsp = self.utils['bs_power']
        apw = self.utils['arm_power']
        opt = self.utils['optical_thickness']
        qtf = self.utils['quad_transfer_functions']
        bsz = self.utils['beam_size']

        # Conditional calculations.
        # Check whether they need to be calculated before they actually are
        # for efficiency.
        # Not externally held, so can see what it depends on
        if 'signal_omega' not in self.parameters.keys() \
        or 'frequency' in parameters.keys():
            self.parameters['signal_omega'] = 2 * np.pi * self.parameters[
                'frequency']
        old_unsettables['signal_omega'] = True

        # Not externally held, so can see what it depends on
        if ('suspension_VH_coupling_theta' not in self.parameters.keys() \
        or 'length' in parameters.keys()) or \
        'suspension_VH_coupling_theta' not in parameters.keys():
            if self.verbose:
                print('Calculating vertical to horizontal coupling angle')
            self.parameters['suspension_VH_coupling_theta'] = np.arcsin(
                self.parameters['length'] /
                (self.constants.Distances['Re'] * pow(10, 3))) 
            old_unsettables['suspension_VH_coupling_theta'] = True

        if self._conditionalCalculation(fin, 'finesse', parameters):
            if self.verbose:
                print('Calculating detector finesse')
            self.parameters['finesse'] = fin.calculate(self)
            old_unsettables['finesse'] = True

        if self._conditionalCalculation(prf, 'power_recycling_factor', parameters) \
        or old_unsettables['finesse']:
            if self.verbose:
                print('Calculating power recycling factor')
            self.parameters['power_recycling_factor'] = prf.calculate(self)
            old_unsettables['power_recycling_factor'] = True

        if self._conditionalCalculation(bsp, 'bs_power', parameters) \
        or old_unsettables['power_recycling_factor']:
            if self.verbose:
                print('Calculating power at the beam splitter')
            self.parameters['bs_power'] = bsp.calculate(self)
            old_unsettables['bs_power'] = True

        if self._conditionalCalculation(apw, 'arm_power', parameters) \
        or old_unsettables['bs_power']:
            if self.verbose:
                print('Calculating power in the arms')
            self.parameters['arm_power'] = apw.calculate(self)
            old_unsettables['arm_power'] = True

        # Not externally held, so can see what it depends on
        if 'mirror_volume' not in self.parameters.keys() \
        or 'mass_radius' in parameters.keys() \
        or 'mass_thickness' in parameters.keys():
            if self.verbose:
                print('Calculating the mirror volume')
            self.parameters['mirror_volume'] \
              = np.pi*pow(self.parameters['mass_radius'], 2) * \
                self.parameters['mass_thickness']
            old_unsettables['mirror_volume'] = True

        # Not externally held, so can see what it depends on
        if 'substrate_mass_density' not in self.parameters.keys() \
        or 'mirror_mass' in parameters.keys() \
        or old_unsettables['mirror_volume']:
            if self.verbose:
                print('Calculating the mirror density')
            self.parameters['substrate_mass_density'] \
              = self.parameters['mirror_mass'][0] / self.parameters['mirror_volume']
            old_unsettables['substrate_mass_density'] = True

        if self._conditionalCalculation(opt, 'itm_coating_optical_thickness',
                                        parameters):
            if self.verbose:
                print('Calculating optical thickness')
            OT = opt.calculate(self)  # m
            self.parameters['itm_coating_optical_thickness'] = OT[0]
            self.parameters['etm_coating_optical_thickness'] = OT[1]

        if self._conditionalCalculation(qtf, 'suspension_htable', parameters) \
        or old_unsettables['suspension_VH_coupling_theta']:
            if self.verbose:
                print(
                    'Calculating table motion and force to mass motion transfer functions'
                )
            TFS = qtf.calculate(self)
            self.parameters['suspension_htable'] = TFS[0]
            self.parameters['suspension_vtable'] = TFS[1]
            self.parameters['suspension_hforce'] = TFS[2]
            self.parameters['suspension_vforce'] = TFS[3]

        if self._conditionalCalculation(bsz, 'itm_beam_radius', parameters):
            if self.verbose:
                print(
                    'Calculating beam radii, beam waist and relative mirror positions'
                )
            spots = bsz.calculate(self)
            self.parameters['itm_beam_radius'] = spots[0]  # m
            self.parameters['itm_position_wrt_waist'] = spots[1]  # m
            self.parameters['etm_beam_radius'] = spots[2]  # m
            self.parameters['etm_position_wrt_waist'] = spots[3]  # m
            self.parameters['gaussian_beam_waist'] = spots[4]  # m

        # Not externally held, so can see what it depends on
        if 'laser_carrier_frequency' not in self.parameters.keys() \
        or 'wavelength' in parameters.keys():
            if self.verbose:
                print('Calculating carrier frequency')
            self.parameters['laser_carrier_frequency'] \
            = 2 * np.pi * self.constants.c / self.parameters['wavelength']

    # Set up aLIGO-specific noise models
    def _set_noise_models(self, noise_models={}):

        IfoParent._set_noise_models(self, noise_models=noise_models)

        # Set aLIGO-specific noise models
        self.noise_models['Seismic'] \
            = SeismicNoise(ifo=self, verbose=self.verbose)

        self.noise_models['Newtonian'] \
            = NewtonianNoise(ifo=self, verbose=self.verbose)

        # Finesse quantum model, comment for standard quantum noise
        self.noise_models['Quantum'] = FinesseQuantumNoise(ifo=self, verbose=self.verbose)

        # Add to or overwrite with any user-defined noise models
        for key in noise_models.keys():
            self.noise_models[key] = noise_models[key]
