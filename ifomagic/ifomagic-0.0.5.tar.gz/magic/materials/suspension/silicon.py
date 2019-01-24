'''
Silicon material class, in_herits from MaterialParent.

References:
--- [1] (for T ~ 120 K)
      http://design.caltech.edu/Research/MEMS/siliconprop.html

--- [2] Gysin et al. Physical Review B (2004)

--- [3] Nawrodt (2010)

MAGIC
@author: Isobel
'''
from magic.materials import MaterialParent

import numpy as np
from scipy.interpolate import interp1d


class Silicon(MaterialParent):

    def __init__(self, properties={}):

        super().__init__(properties=properties)

        # Set up silicon-specific values
        self.properties = {}
        # Density [1], a constant
        self.properties['rho'] = 2330  # kg/m^3
        # Heat capacity [1], temperature dependent
        self.properties['C'] = 772  # J/kg/K
        # Thermal conductivity [1], temperature and geometry dependent
        self.properties['k'] = 4980  # W/m/K
        # Thermal expansion coefficient [1], temperature dependent
        self.properties['alpha'] = 1e-9  # 1/K
        # dlnE/dT [2], temperature dependent on_ly
        self.properties['dlnE_dT'] = 2.5e-10  # 1/K
        # Loss angle [3]
        self.properties['phi'] = 2e-9
        # Young's modulus
        self.properties['Y'] = 150e9  # Pa
        # Division factor for quadruple pendulum
        self.properties['div_fact'] = 16
        # Specific heat, temperature dependent
        self.properties['mass_Cm'] = 739  # J/kg/K

        self.updateProperties(properties)

    def calcNewdlnEdT(self, T):

        # [2]
        # 'E0 is the Young’s modulus at 0 K. The constants B
        # > 0 and T0 > 0 are temperature independent.'
        E0 = 167.5E9  # Pa
        B = 15.8E6  # Pa/K
        T0 = 317  # K

        E = E0 - B * T * np.exp(-T0 / T)

        # Differentiate :
        # dlnE/dT = (1/E) * dE/dT
        # dlnE/dT = (1/E) * - (B*exp(-T0/T) + B*T*(-(-T0/T^2)*exp(-T0/T))
        # dlnE/dT = (1/E) * - (B*exp(-T0/T) + B*(T0/T)*exp(-T0/T))
        # dlnE/dT = - (1/E) * B * exp(-T0/T) * (1 + (T0/T))

        dlnE_dT = -(1 / E) * B * np.exp(-T0 / T) * (1 + (T0 / T))

        return dlnE_dT

    def calcNewAlpha(self, T):

        # [1]
        # Interpolate estimated points on graph,
        # http://www.ioffe.ru/SVA/NSM/Semicond/Si/Figs/156.gif
        T_array = [
            0, 10, 25, 40, 50, 60, 100, 120, 150, 200, 250, 300, 350, 400, 450,
            500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000, 1200, 1400,
            1500
        ]
        alpha_array = [
            0, -0.05, -0.12, -0.22, -0.41, -0.45, -0.3, 1E-4, 0.6, 1.41, 2.22,
            2.69, 3.01, 3.3, 3.45, 3.6, 3.75, 3.82, 3.9, 3.98, 4.07, 4.13,
            4.19, 4.21, 4.23, 4.26, 4.4, 4.5, 4.6
        ]
        alpha_array = [a * 1E-6 for a in alpha_array]
        alpha = interp1d(
            T_array, alpha_array, kind='cubic', fill_value='extrapolate')(T)
        return alpha