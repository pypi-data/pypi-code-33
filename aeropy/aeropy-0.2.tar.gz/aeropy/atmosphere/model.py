#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Python code modelling the Earth's atmosphere
"""


import numpy as np


class ISA:
    """International Standard Atmosphere (ISA) atmospheric model"""

    def __init__(self):
        # Some constants
        self.R = 287
        self.g = 9.81
        self.T_0 = 288.15
        self.rho_0 = 1.225
        self.gamma = 1.4
        self.h = 0
        self.ref_mu = 1.717*10**(-5.)  # Reference viscosity for Sutherland's law
        self.ref_T = 273.15  # Reference temperature for Sutherland's law
        self.ref_S = 110.4  # Reference Sutherland temperature for Sutherland's law
        # Some data
        self.layers = ['Troposphere', 'Tropopause', 'Lower Stratosphere', 'Upper Stratosphere', 'Stratopause',
                       'Lower Mesosphere', 'Upper Mesosphere', 'Mesopause']
        self.altitudes = np.array([0, 11, 20, 32, 47, 51, 71, 84.852]) * 1000
        self.lapse_rates = np.array([-6.5, 0, 1, 2.8, 0, -2.8, -2, 0]) / 1000
        self.pressures = np.array([self.rho_0*self.R*self.T_0, 22632, 5474.9, 868.02, 110.91, 66.939, 3.9564, 0.3734])
        # Some calcs
        altitudes_delta = np.array([self.altitudes[i] - self.altitudes[i - 1] for i in np.arange(0, len(self.altitudes))])
        altitudes_delta[0] = 0
        self.temperatures = np.cumsum(altitudes_delta * np.roll(self.lapse_rates, 1)) + self.T_0

    def temperature(self, h=None):
        if h == None:
            h = self.h
        layer = np.argmax(self.altitudes > h) - 1
        T = self.temperatures[layer] + self.lapse_rates[layer] * (h - self.altitudes[layer])
        if h > self.altitudes[-1]:
            return np.nan
        else:
            return T

    def pressure(self, h=None):
        if h == None:
            h = self.h
        layer = np.argmax(self.altitudes > h) - 1
        if self.lapse_rates[layer] != 0:
            P = self.pressures[layer] * (self.temperature(h) / self.temperatures[layer]) ** (-self.g / (self.R * self.lapse_rates[layer]))
        else:
            P = self.pressures[layer] * np.exp(-self.g * (h - self.altitudes[layer]) / (self.R * self.temperatures[layer]))
        if h > self.altitudes[-1]:
            return np.nan
        else:
            return P

    def density(self, h=None):
        if h == None:
            h = self.h
        rho = self.pressure(h) / self.R / self.temperature(h)
        return rho

    def a(self, h=None):
        if h == None:
            h = self.h
        a = np.sqrt(self.gamma*self.R*self.temperature(h))
        return a

    def dynamic_viscosity(self, h=None):
        if h == None:
            h = self.h
        mu = self.ref_mu*(self.temperature(h)/self.ref_T)**(3./2.)*(self.ref_T+self.ref_S)/(self.temperature(h)+self.ref_S)
        return mu