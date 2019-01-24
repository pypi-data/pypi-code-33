'''
Silica material class, in_herits from MaterialParent.

References:

--- [1] Quartz Glass for Optics Data and Properties, Heraeus data sheet
--- [2] Gretarsson and Harry, Gretarsson thesis

MAGIC
@author: Isobel
'''
from magic.materials import MaterialParent


class Silica(MaterialParent):

    def __init__(self, properties={}):

        super().__init__(properties=properties)

        # Set up silica-specific values
        self.properties = {}
        # Refractive index
        self.properties['r_index'] = 1.45
        # [1] Poisson ratio
        self.properties['sigma'] = 0.167  # kg/m^3
        # [1] Specific heat
        self.properties['C'] = 739  # J/Kg/K
        # [1] Thermal conductivity
        self.properties['k'] = 1.38  # W/m/K
        # [1] Thermal expansion coefficient
        self.properties['alpha'] = 3.9E-7  # 1/K
        # Absorption
        self.properties['absorption'] = 0.3E-4  # 1/m
        # Exponent for frequency dependence of loss
        self.properties['loss_exp'] = 0.77
        # [1] Young's modulus
        self.properties['Y'] = 7.27E10  # N/m^2
        # Coefficient of freq dep term for bulk loss
        self.properties['c2'] = 7.6E-12
        # Surface loss limit
        self.properties['surf_loss_lim'] = 5.2e-12  # [2]

        self.updateProperties(properties)