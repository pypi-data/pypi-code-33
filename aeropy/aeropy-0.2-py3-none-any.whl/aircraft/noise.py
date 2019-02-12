#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Airframe noise modelling module (using Fink's method)
"""


import numpy as np


class Position:
    """
    Defines the position of the noise source with respect to the observer
    """

    def __init__(self, r=1., theta=np.pi / 2., phi=0.):
        self.r = r  # distance source to observer (in m)
        self.theta = theta  # polar directivity angle
        self.phi = phi  # azimuthal directivity angle


class Aircraft:
    """
    Defines the aircraft model needed for the noise modelling process
    Default values are similar to a B737
    """

    def __init__(self, v=81., b=34., S=130., b_flaps=17., S_flaps=18., delta_flaps=30. * np.pi / 180., d_main_tire=1.1,
                 n_main_wheel=2., d_nose_tire = 0.69, n_nose_wheel=2.):
        self.v = v  # airspeed (in m/s)
        self.b = b  # total wing span (in m)
        self.S = S  # wing area (in m^2)
        self.b_flaps = b_flaps  # flap span (in m)
        self.S_flaps = S_flaps  # flap area (in m^2)
        self.delta_flaps = delta_flaps  # flap deflection angle
        self.n_main_wheel = n_main_wheel  # number of wheels per bogie
        self.d_main_tire = d_main_tire  # tire diameter (in m)
        self.n_nose_wheel = n_nose_wheel  # number of wheels per bogie
        self.d_nose_tire = d_nose_tire  # tire diameter (in m)


class Atmosphere:
    """
    Compensatory class for atmospheric properties if the aeropy atmosphere module is not available
    """

    def __init__(self, rho=1.225, a=340.263, mu=1.79e-05 ):
        self.__rho = rho
        self.__a = a
        self.__mu = mu

    def density(self):
        return self.__rho

    def a(self):
        return self.__a

    def dynamic_viscosity(self):
        return self.__mu


class Noise:
    """
    Base class for noise modelling which also provides utility functions
    """

    def __init__(self, aircraft, position, atmosphere):
        """Set up initial problem"""

        self.aircraft = aircraft
        self.position = position
        self.atmosphere = atmosphere
        self.mach = self.aircraft.v / self.atmosphere.a()
        self.n = np.arange(1, 44)  # band numbers
        self.f_n = 10. ** (self.n / 10.)  # center frequencies

    def noise_spectrum_level(self):
        """Calculates the noise spectrum level (in dB)"""

        delta_f = (2. ** (1. / 6.) - 2. ** (-1. / 6.)) * self.f_n
        PSL = self.__noise_pressure_band_level() - 10. * np.log10(delta_f)

        return self.f_n, PSL

    def __noise_pressure_band_level(self):
        """Calculates the noise pressure level per terts band (in dB)"""

        PBL = 10. * np.log10(self.__noise_pressure_squared() / (2. * 10. ** (-5)) ** 2)

        return PBL

    def __noise_pressure_squared(self):
        """Calculates the squared noise pressure per terts band (in Pa^2)"""

        noise_pressure_squared = self.atmosphere.density() * self.atmosphere.a() * self.power_function() * \
                                 self.directivity_function() * self.spectral_function(self.f_n) / \
                                 (4 * np.pi * self.position.r ** 2. * (1. - self.mach * np.cos(self.position.theta)) ** 4.)

        return noise_pressure_squared

    def power_function(self):
        P = self.K * self.mach ** self.a * self.G * self.atmosphere.density() * self.atmosphere.a() ** 3. * \
            self.aircraft.b ** 2
        return P

    def strouhal_function(self, f):
        S = f * self.L * (1. - self.mach * np.cos(self.position.theta)) / self.aircraft.v
        return S


class LandingGearNoise(Noise):

    def __init__(self, *args, **kwargs):
        Noise.__init__(self, *args, **kwargs)
        self.set_gear()

        if self.n_wheel == 1 or self.n_wheel == 2:
            self.K = 4.349 * 10. ** (-4.)
        elif self.n_wheel == 4:
            self.K = 3.414 * 10. ** (-4.)
        self.a = 6.
        self.L = self.d_tire
        self.G = self.n_wheel * (self.d_tire / self.aircraft.b) ** 2.

    def spectral_function(self, f):
        F = self.n_wheel * (13.59 * self.strouhal_function(f) ** 2. * (self.strouhal_function(f) ** 2. + 12.5) ** (-2.25))
        return F

    def directivity_function(self):
        D = 4. * (np.cos(self.position.phi)) ** 2. * (np.cos(self.position.theta / 2.)) ** 2.
        return D


class MainLandingGearNoisePerBogie(LandingGearNoise):

    def set_gear(self):
        self.n_wheel = self.aircraft.n_main_wheel
        self.d_tire = self.aircraft.d_main_tire


class NoseLandingGearNoisePerBogie(LandingGearNoise):

    def set_gear(self):
        self.n_wheel = self.aircraft.n_nose_wheel
        self.d_tire = self.aircraft.d_nose_tire


class FlapNoise(Noise):

    def __init__(self, *args, **kwargs):
        Noise.__init__(self, *args, **kwargs)

        self.K = 2.787 * 10. ** (-4.)
        self.a = 6.
        self.L = self.aircraft.S_flaps / self.aircraft.b_flaps
        self.G = self.aircraft.S_flaps / self.aircraft.b ** 2. * (np.sin(self.aircraft.delta_flaps)) ** 2.

    def spectral_function(self, f):
        S = self.strouhal_function(f)
        F = np.piecewise(S, [S < 2, (S >= 2) & (S <= 20), S > 20],
                         [lambda S: 0.048 * S, lambda S: 0.1406 * S ** (-0.55), lambda S: 216.49 * S ** (-3.)])
        return F

    def directivity_function(self):
        D = 3. * (np.sin(self.aircraft.delta_flaps) * np.cos(self.position.theta) +
                  np.cos(self.aircraft.delta_flaps) * np.sin(self.position.theta) * np.cos(self.position.phi)) ** 2.
        return D


class WingNoise(Noise):

    def __init__(self, *args, **kwargs):
        Noise.__init__(self, *args, **kwargs)

        self.K = 4.464 * 10. ** (-5.)
        self.a = 5.
        self.G = self.aircraft.S / self.aircraft.b ** 2. * ((self.atmosphere.density()*self.aircraft.v*self.aircraft.S)/(self.atmosphere.dynamic_viscosity()*self.aircraft.b)) ** (-0.2)
        self.L = self.G * self.aircraft.b

    def spectral_function(self, f):
        S = self.strouhal_function(f)
        F = 0.613*(10.*S)**4.*((10.*S)**1.5+0.5)**(-4.)
        return F

    def directivity_function(self):
        D = 4. * (np.cos(self.position.phi)) ** 2. * (np.cos(self.position.theta / 2.)) ** 2.
        return D


class SlatNoise(Noise):

    def __init__(self, *args, **kwargs):
        Noise.__init__(self, *args, **kwargs)

        self.K = 4.464 * 10. ** (-5.)
        self.a = 5.
        self.G = self.aircraft.S / self.aircraft.b ** 2. * ((self.atmosphere.density()*self.aircraft.v*self.aircraft.S)/(self.atmosphere.dynamic_viscosity()*self.aircraft.b)) ** (-0.2)
        self.L = self.G * self.aircraft.b

    def spectral_function(self, f):
        S = self.strouhal_function(f)
        F = 0.613*(10.*S)**4.*((10.*S)**1.5+0.5)**(-4.) + 0.613*(2.19*S)**4.*((2.19*S)**1.5+0.5)**(-4.)
        return F

    def directivity_function(self):
        D = 4. * (np.cos(self.position.phi)) ** 2. * (np.cos(self.position.theta / 2.)) ** 2.
        return D
