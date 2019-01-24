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
        # Refractive index
        self.properties['r_index'] = 3.5
        # [1] Poisson ratio
        self.properties['sigma'] = 0.27  # kg/m^3
        # [1] Specific heat
        self.properties['C'] = 0.3 * 1000  # J/kg/K
        # [1] Thermal conductivity
        self.properties['k'] = 700  # W/m/K
        # [1] Thermal expansion coefficient
        self.properties['alpha'] = 1E-9  # 1/K
        # Absorption
        self.properties['absorption'] = 0.3E-4  # 1/m
        # Exponent for frequency dependence of loss
        self.properties['loss_exp'] = 1
        # [1] Young's modulus
        self.properties['Y'] = 155.8E9  # N/m^2
        # Coefficient of freq dep term for bulk loss
        self.properties['c2'] = 3E-13
        # Surface loss limit
        self.properties['surf_loss_lim'] = 5.2e-12  # [2]

        self.updateProperties(properties)

    def calcNewCm(self, T):

        # [1]
        # Interpolate estimated points on graph,
        # http://www.ioffe.ru/SVA/NSM/Semicond/Si/Figs/154.gif
        # Flubacher, P., A. J. Leadbetter, and J. A. Morrison, Phil. Mag. 4, 39 (1959) 273-294
        T_array = [2.5, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, \
                   50, 60, 70, 80, 90, 100, 200, 300, 320]
        Cm_array = [6E-6, 9E-6, 1.8E-5, 3.1E-5, 5E-5, 8E-5, 1.3E-4, 2E-4, 2.9E-4, \
                   4E-3, 1.9E-2, 5.5E-2, 1E-1, 1.5E-1, 1.9E-1, 2.3E-1, 2.5E-1, 2.7E-1, \
                   4.5E-1, 5.35E-1, 5.5E-1]
        Cm_array = [c * 1E3 for c in Cm_array]
        Cm = interp1d(
            T_array, Cm_array, kind='cubic', fill_value='extrapolate')(T)
        return Cm