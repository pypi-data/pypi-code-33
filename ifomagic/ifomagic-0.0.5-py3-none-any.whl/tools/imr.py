'''
IMR model following Ajith et al., "A template bank for
gravitational waveforms from coalescing binary black holes:
non-spinning binaries (2009), and adapted from Isobel Romero-Shaw
gravitational waves group studies code (2017).

Note: This model assumes natural units where G == c == 1

@author: Roshni
'''

import numpy as np
from magic import constants

import matplotlib.pyplot as plt


def setSource(m1, m2):
    source = {}
    source['m1'] = m1 * constants.M_sun * constants.G / (constants.c)**2
    source['m2'] = m2 * constants.M_sun * constants.G / (constants.c)**2
    source['total_mass'] = source['m1'] + source['m2']
    source['symmetric_mass'] = source['m1'] * source['m2'] / pow(
        source['total_mass'], 2.0)
    source['pre_V'] = np.pi * source['total_mass']
    # Transitional frequencies and sigma. Natural units used in equations
    convo = 1 / (np.pi * source['total_mass'])
    source['f_merge'] = (1. - 4.455 + 3.521) * convo
    source['f_ring'] = ((1. - 0.63) / 2.0) * convo
    source['f_cutoff'] = (0.3236) * convo
    source['sigma'] = ((1. - 0.63) / 4.0) * convo
    # Phase expansions
    source[0] = 0.0
    source[1] = 0.0
    source[2] = 3715.0 / 756.0
    source[3] = -16 * np.pi
    source[4] = 15293363.0 / 508032.0
    source[5] = 0.0
    source[6] = 0.0
    source[7] = 0.0
    return source


def inspiralPhenomBAmp(f, source):
    return pow((f/source['f_merge']), -7.0/6.0)*(1.0 +\
                       (-(323./224.)+(451./168.)*source['symmetric_mass'])*\
                       (pow(source['pre_V']*f, 2.0/3.0)))


def mergerPhenomBAmp(f, source):
    wM = getWm(source)
    return np.multiply(wM * pow((f/source['f_merge']), -2.0/3.0),(1 + \
                       (-1.8897*pow(source['pre_V']*f, 1.0/3.0)) + \
                       1.6557*pow((source['pre_V']*f), (2.0/3.0))))


def getWm(source):
    return (1.+(-(323./224.)+(451./168.)*source['symmetric_mass'])
       *pow(source['pre_V']*source['f_merge'], 2.0/3.0)) /(1. + \
           (-1.8897*pow(source['pre_V']*source['f_merge'], 1.0/3.0) + \
            1.6557*pow((source['pre_V']*source['f_merge']), 2.0/3.0)))


def ringdownPhenomBAmp(f, source):
    return (mergerPhenomBAmp(source['f_ring'], source)/ \
            lorentzianFunction(source['f_ring'], source)) \
          *lorentzianFunction(f, source)


def lorentzianFunction(current_freq, source):
    return source['sigma']/(2.0*np.pi*(pow((current_freq - source['f_ring']), 2.0) \
              + pow((source['sigma']/2.0), 2.0)))
              

def phasePhenomB(source, f):
    arrival_time = 0.0
    phase_offset = 0.0
    time_dependence = 2.0 * np.pi * arrival_time * f
    v = pow(source['pre_V'] * f, 1.0 / 3.0)
    phase_sum = 0.0

    for i in range(0, 8):
        phase_sum += pow(v, i) * source[i]

    return -(time_dependence + phase_offset \
   + (3.0/(128.0*source['symmetric_mass']*pow(v, 5.0)))*(1.0 + phase_sum))


def IMRPhenomBModel(source, f):
    # convert to natural units for calculation
    f = f/constants.c
    if f <= source['f_merge']:
        signal = inspiralPhenomBAmp(f, source)
    elif f > source['f_merge'] and f <= source['f_ring']:
        signal = (mergerPhenomBAmp(f, source))
    else:
        signal = (ringdownPhenomBAmp(f, source))


# Inclusion of effective phase arbitrary right now
    wave_phase = phasePhenomB(source, f)
    j = complex(0, 1)
    signal = abs(signal * np.exp(j * wave_phase) / constants.c)
    return signal
