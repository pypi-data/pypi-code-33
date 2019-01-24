'''
File to hold all constants used in MAGIC.
Should be expanded as needed.
In an ideal situation, all numerical constants should be stored here to avoid
slight disrepancies between values from different packages.

References:

MAGIC
@author: Isobel
'''

# Value unset at initialisation warning
UNSET = 'Value not set at initialisation'
# Speed of light (m/s)
c = 299792458
# Gravitational acceleration (m/s^2)
g = 9.80665
# Gravitational constant (m3/kg/s^2)
G = 6.67408E-11
# Mass of the Sun (kg)
M_sun = 1.99E30
# Planck Constant (J/s)
h = 6.626068E-34
# Reduced Planck constant (J/s)
hbar = 1.0545718001391127e-34
# Boltzmann Constant (m^2 kg/s^2/K)
kb = 1.38064852e-23
# Atmospheric pressure (mb)
atmospherePressure = 1013
# Temperature of Nitrogen (K)
nitrogenTemp = 77
# Electron mass
m_e = 9.10938356E-31

Distances = {}
# Distances in km
Distances['Re'] = 6400
Distances['AU'] = 149598000
Distances['PC'] = 3.08568025E16
Distances['KPC'] = 3.08568025E19
Distances['MPC'] = 3.08568025E22