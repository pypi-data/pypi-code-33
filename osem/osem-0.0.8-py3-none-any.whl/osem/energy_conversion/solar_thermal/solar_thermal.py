from math import floor
from math import pow

from osem.general.enerapi.base.base import Base

from osem.general.enerapi.common.Guard import *

__author__ = 'VincentRoch'


class SolarThermal(Base):
    """
    Estimate useful output power of a flat plate solar collector
    """

    _default_parameter_value = {
        "F": 0.7313,
        "c1": 3.74,
        "c2": 0.0076,
    }

    @staticmethod
    def help():
        return SolarThermal.__doc__ + "\r\n" + SolarThermal.calculate.__doc__

    @staticmethod
    def help_calculate():
        return SolarThermal.__init__.__doc__.format(
            SolarThermal._default_parameter_value["F"],
            SolarThermal._default_parameter_value["c1"],
            SolarThermal._default_parameter_value["c2"],
        )

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"GbeamTiltedPlane": 741.4, "GdiffuseTiltedPlane": 76.1,
            "incidentAngle": 24.2, "surface": 9.0, "Ta": 23.6,
            "Tin": 21.0, "Tout": 60.0, "F": 0.7313, "c1": 3.74,
            "c2": 0.0076}}

        {{
            GbeamTiltedPlane      [W/m2]        (must be a positive value)
            GdiffuseTiltedPlane   [W/m2]        (must be a positive value)
            incidentAngle         [deg.]        (must be a positive value
                    between 0 and 180)
            surface               [m2]          (must be a positive value)
            Ta                    [deg.C]       (float)
            Tin                   [deg.C]       (float but smaller than Tout)
            Tout                  [deg.C]       (float bigger than Tin)
            F                     [-]           (must be a positive value)
                    default: {0}
            c1                    [W/(m2*K)]    (must be a positive value)
                    default: {1}
            c2                    [W/(m2*K2)]   (must be a positive value)
                    default: {2}

        }}
        """

        super(SolarThermal, self).__init__(args)

        Guard.check_if_key_in_dict("GbeamTiltedPlane", args)
        Guard.check_if_key_in_dict("GdiffuseTiltedPlane", args)
        Guard.check_if_key_in_dict("incidentAngle", args)
        Guard.check_if_key_in_dict("surface", args)
        Guard.check_if_key_in_dict("Ta", args)
        Guard.check_if_key_in_dict("Tin", args)
        Guard.check_if_key_in_dict("Tout", args)

        Guard.check_value_in_between(args["incidentAngle"], min=0, max=180)

        Guard.check_is_higher(args["GbeamTiltedPlane"], lower_limit=0)
        Guard.check_is_higher(args["GdiffuseTiltedPlane"], lower_limit=0)
        Guard.check_is_higher(args["surface"], lower_limit=0)
        Guard.check_is_higher(args["F"], lower_limit=0)
        Guard.check_is_higher(args["c1"], lower_limit=0)
        Guard.check_is_higher(args["c2"], lower_limit=0)
        Guard.check_is_higher(args["Tout"], lower_limit=args["Tin"])

        self.args = args
        pass

    def calculate(self):
        """

        The returned object is of the form:
        {
            "usefulOutputPower":    [W]     (float)
            "IAMbeam":              [-]     (float)
            "IAMdiffuse":           [-]     (float)
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        GbeamTiltedPlane    [W/m2]      Beam radiance onto the tilted surface (must be a positive value)
        GdiffuseTiltedPlane [W/m2]      Diffuse solar radiance onto the tilted surface (must be a positive value)
        incidentAngle       [deg.]      Angle of incidence, the angle between the beam radiation on a surface and the
                                        normal to that surface. (must be a positive value between 0 and 180)
        surface             [m2]        Surface of the solar collector (must be a positive value)
        Ta                  [deg.C]     Surrounding air temperature
        Tin                 [deg.C]     Collector inlet temperature (must be a positive value smaller than Tout)
        Tout                [deg.C]     Collector outlet temperature (must be a positive value bigger than Tin)
        F                   [-]         Zero loss efficiency (must be a positive value)
        c1                  [W/(m2*K)]  Heat loss coefficient at (Tm - Ta) = 0 (Tm = (Tin + Tout)/2)
            (must be a positive value1)
        c2                  [W/(m2*K2)] Temperature dependence of the heat loss coefficient
            (must be a positive value)


        *********************************************************************
        Outputs:
        *********************************************************************
        usefulOutputPower   [W]     Useful output power of solar collector
        IAMbeam             [-]     Incident Angle Modifier for beam radiance
        IAMdiffuse          [-]     Incident Angle Modifier for diffuse radiance


        *********************************************************************
        Notes:
        *********************************************************************
        The main equation for useful power output is taken and simplified from [1]

        Default values:
        F, c1, c2 are taken from [2], average of 3 collectors:
            "Energie Solaire AS+"
            "Ernst SchweizerFK2-XB-V4"
            "Soltop COBRALINO Evo 2.8H"

        c1 and c2 were taken for gross area (The maximum projected area of a complete solar collector module,
        exclusive of integral means of mounting and connecting fluid conduits.)

        Incident Angle Modifier (IAM) curve for beam radiance (Kb) is taken from [2] (average of the 3 collectors)
        Incident Angle Modifier (IAM) for diffuse (Kd) radiance is taken for incidentAngle = 60 deg.

        *********************************************************************
        References:
        *********************************************************************
        [1] S. Fischer, W. Heidemann, H. Muller-Steinhagen, B. Perers, P. Bergquist, and B. Hellstrom,
            "Collector test method under quasi-dynamic conditions according to the European Standard EN 12975-2"
            Solar Energy, vol. 76, no. 1-3, pp. 117-123, Jan. 2004.
        [2] SPF, Institut Fur SolarTechnik, Collectors, http://www.spf.ch/index.php?id=111&L=6&no_cache=1

        """

        Gb = float(self.args["GbeamTiltedPlane"])
        Gd = float(self.args["GdiffuseTiltedPlane"])
        S = float(self.args["surface"])
        Ta = float(self.args["Ta"])
        F = float(self.args["F"])
        c1 = float(self.args["c1"])
        c2 = float(self.args["c2"])
        t = float(self.args["incidentAngle"])

        # IAM calculation from incidentAngle: interpolation from IAM curve

        # Average data from [2], from incidentAngle = 0 to 90 deg. (step: 5 deg.)
        # ex. t=45 --> IAM=0.9645 or t=85 --> IAM=0.2355
        IAMcurve = [1.0000, 1.0000, 1.0000, 1.0000, 1.0000, 0.9903, 0.9903, 0.9839, 0.9774, 0.9645, 0.9409, 0.9065,
                    0.8548, 0.7860, 0.6903, 0.5742, 0.4204, 0.2355, 0.0000]

        if t >= 90:
            Kb = 0
        else:
            # index related to IAMcurve list: t = 32.5 --> index = floor(32.5/5) = 6
            index = int(floor(t/5.0))

            # Kb calculation --> linear interpolation between 2 incident angles in IAMcurve
            # y = ((Yb-Ya)/(Xb-Xa))*(x-Xa)+Ya)
            Kb = ((IAMcurve[index+1] - IAMcurve[index])/5)*(t-index*5) + IAMcurve[index]

        # Kd calculation (for incidentAngle = 60)
        Kd = IAMcurve[int(60/5)]

        # Mean water temperature in collector
        Tm = (float(self.args["Tin"]) + float(self.args["Tout"])) / 2.0

        # useful output power per m2
        Q = F * Kb * Gb + F * Kd * Gd - c1 * (Tm - Ta) - c2 * pow((Tm - Ta), 2)  # [1]

        # total useful output power
        if Q > 0:
            Qt = Q * S
        else:
            Qt = 0

        return {
            "usefulOutputPower": Qt,
            "IAMbeam": Kb,
            "IAMdiffuse": Kd
        }
