# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
from dx_utilities.units import Mass, Weight


class BaseMaterial(object):
    """Class to represent materials."""

    #: Poisson's ratio
    nu = None
    #: ``[N/m/m/m]``
    weight_density = None
    #: Safety factor
    gamma = None

    def __init__(self):
        self._m = None

    @property
    def w(self):
        """Alias for weight-density ``[N/m/m/m]``.

        :rtype: Weight
        """
        return self.weight_density

    @property
    def m(self):
        """Mass density ``[kg/m/m/m]``.

        :rtype: Mass
        """
        if self._m is None:
            self._m = self.w.to_mass()
        return self._m

    def safety_factor(self, design_situation='persistent',
                      limit_state='ultimate'):
        """Wrapper around the safety factor of the material.
        Returns the value depending on the design situation
        and the limit state considered.

        :param str design_situation:
        :param str limit_state:
        :rtype: float
        """
        return getattr(getattr(self.gamma, design_situation), limit_state)


class BaseReinforcementSteel(BaseMaterial):

    #: Poisson's ratio
    nu = 0.3
    #: ``[N/m/m/m]``
    weight_density = 77078

    def __init__(self):
        self._E = 200 # Modulus of elasticity [GPa]

    @property
    def E(self):
        """Modulus of elasticity ``[N/m/m]``."""
        return self._E*1e+09

    @property
    def G(self):
        """Shear modulus ``[N/m/m]``."""
        return self.E / 2 / (1 + self.nu)
