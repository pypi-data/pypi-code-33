'''
C70 steel material class, in_herits from MaterialParent.

References:

MAGIC
@author: Isobel
'''
from magic.materials import MaterialParent


class C70Steel(MaterialParent):

    def __init__(self, properties={}):

        super().__init__(properties=properties)

        # Set up c70steel-specific values
        self.properties = {}
        # Density
        self.properties['rho'] = 7800  # Kg/m^3
        # Heat capacity
        self.properties['C'] = 486  # J/Kg/K
        # Thermal conductivity
        self.properties['k'] = 49  # W/m/K
        # Thermal expansion coefficient
        self.properties['alpha'] = 12e-6  # 1/K
        # dlnE/dT
        self.properties['dlnE_dT'] = -2.5e-4  # 1/K
        # Loss angle
        self.properties['phi'] = 2e-4
        # Young's modulus
        self.properties['Y'] = 212e9  # Pa

        self.updateProperties(properties)