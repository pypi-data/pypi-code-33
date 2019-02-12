#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Example of airframe noise modeling
"""


import numpy as np
import matplotlib.pyplot as plt
import aeropy.atmosphere.model
import aeropy.aircraft.noise


# Initialize model
atmosphere = aeropy.atmosphere.model.ISA()
#atmosphere = aeropy.aircraft.noise.Atmosphere()
position = aeropy.aircraft.noise.Position()
aircraft = aeropy.aircraft.noise.Aircraft()

# Initialize noise componente and get noise spectrum levels
f, wing_level = aeropy.aircraft.noise.WingNoise(aircraft, position, atmosphere).noise_spectrum_level()
f, slats_level = aeropy.aircraft.noise.SlatNoise(aircraft, position, atmosphere).noise_spectrum_level()
f, flaps_level = aeropy.aircraft.noise.FlapNoise(aircraft, position, atmosphere).noise_spectrum_level()
f, main_landing_gear_level = aeropy.aircraft.noise.MainLandingGearNoisePerBogie(aircraft, position, atmosphere).noise_spectrum_level()
f, nose_landing_gear_level = aeropy.aircraft.noise.NoseLandingGearNoisePerBogie(aircraft, position, atmosphere).noise_spectrum_level()

# Main gear noise spectrum level is actually higher due to two boogies
main_landing_gear_level =10.*np.log10(2.*10.**(main_landing_gear_level/10.))

# Calculate total
total_level = 10.*np.log10(10.**(wing_level/10.)+10.**(slats_level/10.)+10.**(flaps_level/10.)+10.**(main_landing_gear_level/10.)+10.**(nose_landing_gear_level/10.))

# Load reference
data = np.loadtxt('noise_modelling.dat')

# Plotting
plt.figure()
plt.title('airframe noise')
plt.ylabel('spectrum level (in dB)')
plt.xlabel('frequency (in Hz)')
plt.xlim(data[0][1], data[0][-1])
ax = plt.subplot(111)
ax.set_xscale('log')
ax.plot(data[0], data[1], label='measured aircraft noise')
ax.plot(f, total_level, label='modelled total airframe noise')
ax.plot(f, wing_level, label='modelled wing noise')
ax.plot(f, slats_level, label='modelled main slat noise')
ax.plot(f, flaps_level, label='modelled main flap noise')
ax.plot(f, main_landing_gear_level, label='modelled main landing gear noise')
ax.plot(f, nose_landing_gear_level, label='modelled nose landing gear noise')
plt.legend()
plt.show()
