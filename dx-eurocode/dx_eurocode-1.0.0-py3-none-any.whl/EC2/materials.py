"""Library of materials supported in EC2.

All properties for classes defined here
return values expressed in the fundamental
units of the metric system ``[kg, m, s, C]``
and their derivatives ``[N, Pa]``.
"""
import functools
import math

from .safety_factors import CONCRETE_SAFETY_FACTOR, STEEL_SAFETY_FACTOR
from dx_base.exceptions import UnrecognizedMaterialError
from .formulas import nu66N
from dx_utilities.units import (transform_units, transform_value,
                             inverse_transform_value, Weight)
from dx_utilities.data_structures import TolerantDict

from dx_base.materials import BaseMaterial, BaseReinforcementSteel


#: Map of cylinder- to cube-strength of concrete ``[MPa]``.
CYLINDER_TO_CUBE_STRENGTHS = dict(zip(
    (12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90),
    (15, 20, 25, 30, 37, 45, 50, 55, 60, 67, 75, 85, 95, 105),
    ))


class Concrete(BaseMaterial):
    """Generic representation of concrete.

    :param int fck: Characteristic strengh (cylinder) ``[MPa]``.
    :raises UnrecognizedMaterialError: If given cylinder strength is not
        supported by EC2.
    """

    #: Poisson's ratio
    nu = 0.2
    #: ``[N/m/m/m]``
    weight_density = Weight(24e+03)
    #: Safety factor
    gamma = CONCRETE_SAFETY_FACTOR

    def __init__(self, fck, *args, **kwargs):
        if fck not in CYLINDER_TO_CUBE_STRENGTHS:
            raise UnrecognizedMaterialError(3000, (f"No concrete class "
                                                   f"corresponds to {fck} MPa "
                                                   f"cylinder strength"))
        super().__init__(*args, **kwargs)
        self._fck_raw = fck
        self._fck_cube_raw = CYLINDER_TO_CUBE_STRENGTHS[fck]

        # Cached properties
        self._fck = None
        self._fck_cube = None
        self._fcm = None
        self._fctm = None
        self._fctk5 = None
        self._fctk95 = None
        self._Ecm = None
        self._ec1 = None
        self._ecu1 = None
        self._ec2 = None
        self._ecu2 = None
        self._n = None
        self._ec3 = None
        self._ecu3 = None

    def __repr__(self):
        return (f'<{self.__class__.__name__}> '
                f'C{self._fck_raw}/{self._fck_cube_raw}')

    @property
    @transform_units()
    def fck(self):
        """Characteristic cylinder compressive strength ``[Pa]``.

        :rtype: float
        """
        if self._fck is None:
            self._fck = self._fck_raw
        return self._fck

    @property
    @transform_units()
    def fck_cube(self):
        """Characteristic cubic compressive strength ``[Pa]``.

        :rtype: float
        """
        if self._fck_cube is None:
            self._fck_cube = self._fck_cube_raw
        return self._fck_cube

    @property
    @transform_units()
    def fcm(self):
        """Mean compressive strength ``[Pa]``.

        :rtype: float
        """
        if self._fcm is None:
            self._fcm = inverse_transform_value(self.fck) + 8
        return self._fcm

    @property
    @transform_units()
    def fctm(self):
        """Mean tensile strength ``[Pa]``.

        :rtype: float
        """
        if self._fctm is None:
            fck = inverse_transform_value(self.fck)
            if fck <= 50:
                self._fctm = 0.3 * fck**(2/3)
            else:
                fcm = inverse_transform_value(self.fcm)
                self._fctm = 2.12 * math.log(1 + fcm/10)
        return self._fctm

    @property
    @transform_units()
    def fctk5(self):
        """5% percentile of characteristic tensile strength ``[Pa]``.

        :rtype:float
        """
        if self._fctk5 is None:
            fctm = inverse_transform_value(self.fctm)
            self._fctk5 = 0.7 * fctm
        return self._fctk5

    @property
    @transform_units()
    def fctk95(self):
        """95% percentile of characteristic tensile strength ``[Pa]``.

        :rtype:float
        """
        if self._fctk95 is None:
            fctm = inverse_transform_value(self.fctm)
            self._fctk95 = 1.3 * fctm
        return self._fctk95

    @property
    @transform_units(prefix='G')
    def Ecm(self):
        """Secant elastic modulus ``[Pa]``.

        :rtype: float
        """
        if self._Ecm is None:
            fcm = inverse_transform_value(self.fcm)
            self._Ecm = 22 * (fcm/10)**0.3
        return self._Ecm

    @property
    @transform_units(prefix='m')
    def ec1(self):
        """Compressive strain at peak stess ``fc``.

        :rtype: float
        """
        if self._ec1 is None:
            fcm = inverse_transform_value(self.fcm)
            self._ec1 = min(0.7 * fcm**0.31, 2.8)
        return self._ec1

    @property
    @transform_units(prefix='m')
    def ecu1(self):
        """Ultimate compressive strain.

        :rtype: float
        """
        if self._ecu1 is None:
            fck = inverse_transform_value(self.fck)
            if fck < 50:
                self._ecu1 = 3.5
            else:
                fcm = inverse_transform_value(self.fcm)
                self._ecu1 = 2.8 + 27*((98 - fcm)/100)**4
        return self._ecu1

    @property
    @transform_units(prefix='m')
    def ec2(self):
        """Design compressive strain at peak stress ``[Pa]``

        :rtype: float
        """
        if self._ec2 is None:
            fck = inverse_transform_value(self.fck)
            if fck < 50:
                self._ec2 = 2.
            else:
                self._ec2 = 2. + 0.085*(fck - 50)**0.53

        return self._ec2

    @property
    @transform_units(prefix='m')
    def ecu2(self):
        """Design utlimate compressive strain ``[Pa]``

        :rtype: float
        """
        if self._ecu2 is None:
            fck = inverse_transform_value(self.fck)
            if fck < 50:
                self._ecu2 = 3.5
            else:
                self._ecu2 = 2.6 + 35*((90 - fck)/100)**4

        return self._ecu2

    @property
    def n(self):
        """Exponent at Eq. (3.17).

        :rtype: float
        """
        if self._n is None:
            fck = inverse_transform_value(self.fck)
            if fck < 50:
                self._n = 2.
            else:
                self._n = 1.4 + 23.4*((90 - fck)/100)**4

        return self._n

    @property
    @transform_units(prefix='m')
    def ec3(self):
        """Design compressive strain at peak stress assuming
        bi-linear stress-strain relationship (see § 3.1.7(2))
        ``[Pa]``.

        :rtype: float
        """
        if self._ec3 is None:
            fck = inverse_transform_value(self.fck)
            if fck < 50:
                self._ec3 = 1.75
            else:
                self._ec3 = 1.75 + 0.55*((fck - 50)/40)

        return self._ec3

    @property
    @transform_units(prefix='m')
    def ecu3(self):
        """Design ultimate compressive strain at peak stress
        assuming bi-linear stress-strain relationship (see § 3.1.7(2))
        ``[Pa]``.

        :rtype: float
        """
        if self._ecu3 is None:
            fck = inverse_transform_value(self.fck)
            if fck < 50:
                self._ecu3 = 3.5
            else:
                self._ecu3 = 2.6 + 35*((90 - fck)/100)**4

        return self._ecu3

    def CRdc(self, design_situation='persistent',
             limit_state='ultimate'):
        """Factor used in the evaluation of shear capacity.
        See, for example, Eq. (6.47) and Eq. (6.2a)

        :param str design_situation:
        :param str limit_state:
        :rtype: float
        """
        return 0.18 / self.safety_factor(design_situation, limit_state)

    def fcd(self, design_situation='persistent', limit_state='ultimate'):
        """Design strength of the material ``[Pa]``.

        :param str design_situation:
        :param str limit_state:
        :rtype: float
        """
        return self.fck / self.safety_factor(design_situation, limit_state)

    def vrdmax(self, design_situation='persistent', limit_state='ultimate'):
        """Maximum design shear stress evaluated from Eq. (6.5) ``[Pa]``.

        :param str design_situation:
        :param str limit_state:
        :rtype: float
        """
        fck = inverse_transform_value(self.fck)
        return 0.5 * nu66N(fck) * self.fcd(design_situation, limit_state)


class ReinforcedConcrete(Concrete):

    #: ``[N/m/m/m]``
    weight_density = 25e+03


#: Concrete types supported by EC2
RC = TolerantDict(
    {fck: ReinforcedConcrete(fck) for fck in CYLINDER_TO_CUBE_STRENGTHS},
    emsg=f'Unknown concrete class'
    )


class ReinforcementSteel(BaseReinforcementSteel):
    """Represent types of reinforcement steel.

    :param float fyk: Characteristic yield strength [MPa].
    :param float ft: Ultimate tensile strength [MPa].
    :param float eu: Ultimate strain [%].
    """

    #: Safety factor
    gamma = STEEL_SAFETY_FACTOR

    def __init__(self, fyk, ft=None, eu=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fyk = fyk
        self._ft = ft
        self._eu = eu

    @property
    @transform_units()
    def fyk(self):
        """Characteristic yield strength ``[Pa]``.

        :rtype: float
        """
        return self._fyk

    @property
    @transform_units()
    def ft(self):
        """Ultimate tensile strength ``[Pa]``.

        :rtype: float
        """
        if self._ft is None:
            self._ft = 1.05 * self.fyk*1e-06
        return self._ft

    @property
    @transform_units('c')
    def eu(self):
        """Ultimate strain ``[-]``.

        :rtype: float
        """
        if self._eu is None:
            self._eu = 2.5
        return self._eu

    def fyd(self, design_situation='persistent', limit_state='ultimate'):
        """The design yield strength ``[Pa]``.

        :rtype: float
        """
        return self.fyk / self.safety_factor(design_situation, limit_state)
