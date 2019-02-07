# coding=utf-8
from osem.general.enerapi.base.base import Base
from osem.general import conf
from osem.general.enerapi.common.Guard import *

__author__ = 'VincentRoch'


class SolarPV(Base):
    """
    Estimate the electric power production from a photovoltaic module, from Nominal Power of the module, Solar radiance
    and Ambient temperature (optional: Radiance at standard conditions, Temperature coefficient for module efficiency,
    NOCT and Cell temperature at standard conditions)
    """

    _default_parameter_value = {
        "Gstc": 1000.0,
        "TempCoef": 0.5,
        "NOCT": 45.0,
        "Tstc": 25.0,
    }

    @staticmethod
    def help():
        return SolarPV.__doc__ + "\r\n" + SolarPV.calculate.__doc__

    @staticmethod
    def help_calculate():
        return SolarPV.__init__.__doc__.format(
            SolarPV._default_parameter_value["Gstc"],
            SolarPV._default_parameter_value["TempCoef"],
            SolarPV._default_parameter_value["NOCT"],
            SolarPV._default_parameter_value["Tstc"],
        )

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"Pmax": 255.0, "GtotalTiltedPlane": 736.1, "Ta": 23.6, "Gstc": 1000.0,
            "TempCoef": 0.5, "NOCT": 45.0, "Tstc": 25.0}}

        {{
            Pmax               [W]        (must be a positive value),
            GtotalTiltedPlane  [W/m2]     (must be a positive value),
            Ta                 [deg.C]    (must be a value between -50 and 90),
            Gstc               [W/m2]     (must be a strictly positive value)
                    default: {0},
            TempCoef           [%/deg.C]  (must be a positive value)
                    default: {1},
            NOCT               [deg.C]    (must be a positive value)
                    default: {2},
            Tstc               [deg.C]    (must be a positive value)
                    default: {3},
        }}
        """

        super(SolarPV, self).__init__(args)

        Guard.check_if_key_in_dict("Pmax", args)
        Guard.check_if_key_in_dict("GtotalTiltedPlane", args)
        Guard.check_if_key_in_dict("Ta", args)

        Guard.check_is_higher(args["Pmax"], lower_limit=0)
        Guard.check_is_higher(args["GtotalTiltedPlane"], lower_limit=0)
        Guard.check_is_higher(args["Gstc"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["TempCoef"], lower_limit=0)
        Guard.check_value_in_between(args["Ta"], min=-50, max=90)
        Guard.check_is_higher(args["NOCT"], lower_limit=0)
        Guard.check_is_higher(args["Tstc"], lower_limit=0)


        self.args = args
        pass

    def calculate(self):
        """

        The returned object is of the form:
        {
            "ElectricOutputPower":    [W]     (float)
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        Pmax                [W]         Nominal Power of the module (must be a positive value),
        GtotalTiltedPlane   [W/m2]      Total radiance onto a tilted surface (must be a positive value)
        Ta                  [deg.C]     Surrounding air temperature (must be a positive value between -50 and 90)
        Gstc                [W/m2]      Radiance at standard condition, usually 1000 [W/m2]
        TempCoef            [%/deg.C]   Nominal Power temperature coefficient, usually 0.5 [%/deg.C]
        NOCT                [deg.C]     Nominal Operating Cell Temperature, usually 45 [deg.C]
        Tstc                [deg.C]     Cell temperature at standard conditions  usually 25 [deg.C]


        *********************************************************************
        Outputs:
        *********************************************************************
        ElectricOutputPower   [W]   Electric output power (float)


        *********************************************************************
        Notes:
        *********************************************************************
        The two equations for electric power output is taken from [1] and [2] chapter 7.9.1

        Default values:
        Gstc and Tstc are the standard value for PV module testing:
            Gstc = 1000 [W/m2]
            Tstc = 25 [deg.C]
        TempCoef and NOCT are usual values as described in [2]:
            TempCoef = 0.5 [%/deg.C]
            NOCT = 45  [deg.C]


        *********************************************************************
        References:
        *********************************************************************
        [1] EMD international A/S, "Solar Collectors and Photovolotaic in energyPro", 2013
        [2] A. Luque and S. Hegedus, Eds., Handbook of photovoltaic science and engineering. Hoboken, NJ: Wiley, 2003.


        """

        Pmax = float(self.args["Pmax"])
        Gs = float(self.args["GtotalTiltedPlane"])
        Ta = float(self.args["Ta"])
        Gstc = float(self.args["Gstc"])
        TempCoef = float(self.args["TempCoef"])
        NOCT = float(self.args["NOCT"])
        Tstc = float(self.args["Tstc"])

        # Operating cell temperature [deg.C] calculation
        Tcell = Ta + Gs*((NOCT-20)/800.0)  # [2]

        # Electric output power calculation
        ElectricOutputPower = Pmax * Gs/Gstc * (1 - (TempCoef/100.0)*(Tcell-Tstc))  # [1] and [2]

        return {
            "ElectricOutputPower": ElectricOutputPower
        }


    def get_reference(self):
        """
        get the scientific reference for this module
        """
        return conf.ref_solar_pv
