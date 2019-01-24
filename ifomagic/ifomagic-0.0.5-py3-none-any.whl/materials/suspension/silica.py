'''
Silica material class, in_herits from MaterialParent.

TODO: Provide links to these 
References:
--- [1] LIGO-T000012-00-D

--- [2] Fejer et al

--- [3] Quartz Glass for Optics Data and Properties, Heraeus data sheet

--- [4] Gretarsson and Harry, Gretarsson thesis

MAGIC
@author: Isobel
'''
from magic.materials import MaterialParent


class Silica(MaterialParent):

    def __init__(self, properties={}):

        super().__init__(properties=properties)

        # Set up silica-specific values
        self.properties = {}
        # Density
        self.properties['rho'] = 2200  # Kg/m^3
        # Heat capacity
        self.properties['C'] = 772  # J/Kg/K
        # Thermal conductivity
        self.properties['k'] = 1.38  # W/m/K
        # Thermal expansion coefficient
        self.properties['alpha'] = 3.9e-7  # 1/K
        # dlnE/dT
        self.properties['dlnE_dT'] = 1.52e-4  # 1/K
        # Loss angle
        self.properties['phi'] = 4.1e-10
        # Young's modulus
        self.properties['Y'] = 72e9  # Pa
        # Dissipation depth
        self.properties['dissipation_depth'] = 1.5E-2  # m
        # Division factor for quadruple pendulum
        self.properties['div_fact'] = 1

        self.updateProperties(properties)
