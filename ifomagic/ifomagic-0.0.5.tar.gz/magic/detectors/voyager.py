'''
Class containing Voyager interferometer parameters, with many automatically 
in_herited from its parent aLIGO model.

IRS TODO complete references

References:
--- [1] 
   10.1116/1.1479360

--- [2] 
   http://www.ioffe.ru/SVA/NSM/Semicond/Si/index.html (T ~ 120K)
--- [3] Ghosh et al (1994) (123K, 2000nm)
    http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=317500
--- [4] GWINC data

MAGIC
@author: Isobel
'''
from magic.detectors import aLIGO

from magic.noise.ligo import CarrierDensityNoise
from magic.noise.ligo import ThermoRefractiveNoise
import magic
import numpy as np

from scipy.io import loadmat

from copy import deepcopy
import os


class Voyager(aLIGO):

    # Initialisation
    def __init__(self,
                 f=None,
                 xlim=None,
                 ylim=None,
                 parameters={},
                 verbose=False):

        # Use aLIGO defaults
        aLIGO.__init__(
            self,
            f=f,
            xlim=xlim,
            ylim=ylim,
            parameters=parameters,
            verbose=verbose)

    # Treat as private
    # Initialise parameters
    def _initialise_parameters(self, parameters={}):

        aLIGO._initialise_parameters(self)

        # Optimal run parameters (GWINC)
        zz = loadmat(os.path.dirname(magic.__file__) + '/data/ligo/20160824T161306.mat')

        # Basics
        self.parameters['wavelength'] = 2000E-9  # m
        self.parameters['power'] = zz['x'][0][0]  # W
        self.parameters['temperature'] = 295  # K

        # Mass
        self.parameters['mirror_mass'] = [143, 33.74, 41.71, 51.55]  # kg

        self.parameters['mass_radius'] = 0.450 / 2  # m
        self.parameters['mass_thickness'] = 0.55  # m
        # Suspension
        self.parameters['suspension_fiber_type'] = 'ribbon'
        self.parameters['suspension_temperature'] = [300, 300, 300, 123]  # K
        T = self.parameters['suspension_temperature'][-1]
        self.parameters['suspension_length'] = [
            0.4105, 0.4105, 0.4105, 0.4105
        ]  # m
        self.parameters['suspension_ribbon_width'] = 1150E-6  # m
        self.parameters['suspension_ribbon_thickness'] = 115E-6  # m

        # Seismic
        self.parameters['seismic_beta'] = 1
        self.parameters[
            'seismic_omicron'] = 10  # Feedforward cancellation factor

        # Mirror
        self.parameters['itm_curvature'] = 1800  # m
        self.parameters['etm_curvature'] = 2500  # m
        self.parameters['itm_transmittance'] = zz['x'][0][
            3]  # transmittance of ITM
        self.parameters['srm_transmittance'] = zz['x'][0][
            4]  # transmittance of SRM


        # Residual gas
        self.parameters['residual_gas_polarizability'] = 8.1E-31  # [1]

        # Substrate
        self.parameters['substrate_temperature'] = 123  # K
        # Coating
        # High-n
        self.parameters['coating_highn_Y'] = 80E9  # N/m^2, Youngs modulus
        self.parameters['coating_highn_index'] = 3.5
        self.parameters['coating_highn_phi'] = 3E-5
        self.parameters['coating_highn_sigma'] = 0.22  # kg/m^3, Poisson ratio
        self.parameters['coating_highn_alpha'] = 1E-9  # zero crossing at 123 K
        self.parameters['coating_highn_beta'] = 1.4E-4  # dn/dT
        self.parameters[
            'coating_highn_CV'] = 345.6 * 2250  # J/K/m^3, volume-specific heat capacity
        self.parameters['coating_highn_thermal_conductivity'] = 1
        # Low-n
        self.parameters['coating_lown_index'] = 1.436  # [3]
        self.parameters['coating_lown_phi'] = 1E-4

        # Optics and power
        self.parameters['optical_loss'] = 1E-5  # average per mirror power loss

        # Squeezer
        self.parameters['squeezer_type'] = 'frequency dependent'
        self.parameters['frequency_dependent_squeezing'] = True
        self.parameters['squeezer_filter_cavity_f_detune'] = zz['x'][0][
            1]  # Hz
        self.parameters['squeezer_filter_cavity_l'] = 300  # cavity length
        self.parameters['squeezer_amplitude_db'] = 10 # squeezer amplitude
        self.parameters['squeezer_filter_cavity_T_im'] = zz['x'][0][
            2]  # input mirror trasmission
        self.parameters['squeezer_squeeze_angle'] = np.pi / 2  # SQZ phase [radians]
        self.parameters[
            'squeezer_filter_cavity_T_em'] = 0E-6  # end mirror trasmission
        self.parameters['squeezer_filter_cavity_round_trip_loss'] = 10E-6
        self.parameters[
            'squeezer_filter_cavity_rot'] = 0 * np.pi / 180  # phase rotation after cavity
        self.parameters['quad_readoutput_phase'] = zz['x'][0][
            5]  # homoDyne readout phase
        # Output filter

        # Location

        # Materials
        # Use new silicon properties for Voyager [2]
        newsilicon = {
            'rho':
            2329,  # kg/m^3
            'C':
            300,  # J/kg/K
            'k':
            700,  # W/m/K
            #'alpha' : 1E-10,  # 1/K
            'alpha':
            self.parameters['materials']['suspension']['silicon'].calcNewAlpha(
                T),
            #'dlnE_dT' : -2E-5,  # 1/K
            'dlnE_dT':
            self.parameters['materials']['suspension']['silicon']
            .calcNewdlnEdT(T),
            'Y':
            155.8E9,  # Pa
            'phi':
            2E-9,
            'dissipation_depth':
            1.5E-3  # m
        }
        self.parameters['materials']['suspension']['silicon'].updateProperties(
            newsilicon)
        # Fiber material
        self.parameters['suspension_fiber_material'] \
        = self.parameters['materials']['suspension']['silicon']
        # Reset some parameters
        newmirror = {
            'C':
            self.parameters['materials']['mirror']['silicon'].calcNewCm(
                self.parameters['substrate_temperature']),
            'electron_diffusion':
            97 * 1E-4,  # m^2/s
            'hole_diffusion':
            35 * 1E-4,  # m^2/s
            'electron_effective_mass':
            1.07 * self.constants.m_e,  # kg
            'hole_effective_mass':
            0.88 * self.constants.m_e,  # kg
            'carrier_density':
            1E13 * 1E6,  # 1/m^3
            'electron_index_gamma':
            -8.8E-22 * 1E-6,  # m^3
            'hole_index_gamma':
            -10.2e-22 * 1E-6,  # m^3
            'dn_dT':
            1E-4
        }
        self.parameters['materials']['mirror']['silicon'].updateProperties(
            newmirror)
        # Mirror material
        self.parameters['substrate_material'] \
        = self.parameters['materials']['mirror']['silicon']

        # Update settable parameter names
        self.variable_keys = deepcopy(list(self.parameters.keys()))

        aLIGO._update_parameters(self, parameters)

    # Perform calculations
    def _performCalculations(self, parameters={}):

        aLIGO._performCalculations(self, parameters)

        if self.verbose:
            print('Fetching optical thickness')
        itm_ot = loadmat(os.path.dirname(magic.__file__) + '/data/ligo/ITM_layers_151221_2237.mat')
        etm_ot = loadmat(os.path.dirname(magic.__file__) + '/data/ligo/ETM_layers_151221_2150.mat')
        self.parameters['itm_coating_optical_thickness'] = itm_ot['TNout'][
            'L'][0][0].T
        self.parameters['etm_coating_optical_thickness'] = etm_ot['TNout'][
            'L'][0][0].T

        if 'suspension_temperature' in parameters:
            if self.verbose:
                print(
                    'Recalculating suspension temperature-dependent parameters'
                )
            T = parameters['suspension_temperature'][-1]
            new_dlnE_dT = self.parameters['materials']['suspension']['silicon'].calcNewdlnEdT(T)
            new_alpha = self.parameters['materials']['suspension']['silicon'].calcNewAlpha(T)
            new_dict = {'dlnE_dT': new_dlnE_dT, 'alpha': new_alpha}
            self.parameters['materials']['suspension']['silicon'].updateProperties(new_dict)

        if 'substrate_temperature' in parameters:
            if self.verbose:
                print(
                    'Recalculating suspension temperature-dependent parameters'
                )
            T = parameters['substrate_temperature']
            self.parameters['materials']['mirror']['C'] = self.parameters[
                'materials']['mirror']['silicon'].calcNewCm(T)

    # Set Voyager-specific noise models
    def _set_noise_models(self, noise_models={}):

        aLIGO._set_noise_models(self, noise_models)

        # Set up Voyager-specific noise models
        self.noise_models['ITM Carrier Density']\
        = CarrierDensityNoise(ifo=self, verbose=self.verbose)
        self.noise_models['ITM Thermo-Refractive']\
        = ThermoRefractiveNoise(ifo=self, verbose=self.verbose)

        # Add to or overwrite with any user-defined noise models
        for key in noise_models.keys():
            self.noise_models[key] = noise_models[key]
