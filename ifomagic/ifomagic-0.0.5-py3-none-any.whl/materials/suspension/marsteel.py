'''
Maraging steel material class, in_herits from MaterialParent.

References:

MAGIC
@author: Isobel
'''
from magic.materials import MaterialParent


class MaragingSteel(MaterialParent):

    def __init__(self, properties={}):

        super().__init__(properties=properties)

        # Set up maraging steel-specific values
        self.properties = {}
        # Density
        self.properties['rho'] = 7800  # Kg/m^3
        # Heat capacity
        self.properties['C'] = 460  # J/Kg/K
        # Thermal conductivity
        self.properties['k'] = 20  # W/m/K
        # Thermal expansion coefficient
        self.properties['alpha'] = 11e-6  # 1/K
        # dlnE/dT
        self.properties['dlnE_dT'] = 0  # 1/K
        # Loss angle
        self.properties['phi'] = 1e-4
        # Young's modulus
        self.properties['Y'] = 187e9  # Pa

        self.updateProperties(properties)