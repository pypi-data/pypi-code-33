# coding=utf-8
from osem.general import conf
from osem.general.enerapi.base.base import Base
from osem.energy_conversion.solar_thermal.solar_thermal import SolarThermal
from osem.natural_resources.solar.solar_function_incident_angle import SolarFunctionIncidentAngle
from osem.natural_resources.solar.solar_function_radiance_onto_tilted_plane import \
    SolarFunctionRadianceOntoTiltedPlane

from osem.general.enerapi.common.Guard import *

__author__ = 'VincentRoch'


class SolarThermalProductionFromRadiation(Base):
    """
    Estimate useful output power of a flat plate solar collector
    """

    _default_parameter_value = {
        "albedo": SolarFunctionRadianceOntoTiltedPlane._default_parameter_value["albedo"],
        "F": SolarThermal._default_parameter_value["F"],
        "c1": SolarThermal._default_parameter_value["c1"],
        "c2": SolarThermal._default_parameter_value["c2"],
    }

    @staticmethod
    def help():
        return SolarThermalProductionFromRadiation.__doc__ + "\r\n" + \
               SolarThermalProductionFromRadiation.calculate.__doc__

    @staticmethod
    def help_calculate():
        return SolarThermalProductionFromRadiation.__init__.__doc__.format(
            SolarThermalProductionFromRadiation._default_parameter_value["albedo"],
            SolarThermalProductionFromRadiation._default_parameter_value["F"],
            SolarThermalProductionFromRadiation._default_parameter_value["c1"],
            SolarThermalProductionFromRadiation._default_parameter_value["c2"],
        )

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"latitude": 46.100458, "dayOfYear": 235, "solarTime": 13.77,
            "slope": 35.0, "orientation": 45.0, "GbeamH": 850.4,
            "GdiffuseH": 126.3, "Ta": 23.6, "albedo": 0.2,
            "surface": 9.0, "Tin": 21.0, "Tout": 60.0, "F": 0.7313,
            "c1": 3.74, "c2": 0.0076}}

        {{
            latitude        [deg.]      (must be a positive value
                    between -90 and 90)
            dayOfYear       [day]       (must be a positive integer
                    value between 1 and 365)
            solarTime       [hour]      (must be a positive float
                    between 0 and 24)
            slope           [deg.]      (must be a positive value
                    between 0 and 180)
            orientation     [deg.]      (must be a positive value
                    -180 and 180)
            GbeamH          [W/m2]      (must be a positive float),
            GdiffuseH       [W/m2]      (must be a positive value),
            Ta              [deg.C]     (float),
            albedo          [-]         (must be a positive value)
                    default: {0},
            surface         [m2]        (must be a positive value),
            Tin             [deg.C]     (float smaller than Tout),
            Tout            [deg.C]     (float bigger than Tint),
            F               [-]         (positive float)
                    default: {1},
            c1              [W/(m2*K)]  (positive float)
                    default: {2},
            c2              [W/(m2*K2)] (positive float)
                    default: {3},

        }}
        """

        super(SolarThermalProductionFromRadiation, self).__init__(args)

        Guard.check_if_key_in_dict("latitude", args)
        Guard.check_if_key_in_dict("dayOfYear", args)
        Guard.check_if_key_in_dict("solarTime", args)
        Guard.check_if_key_in_dict("slope", args)
        Guard.check_if_key_in_dict("orientation", args)
        Guard.check_if_key_in_dict("GbeamH", args)
        Guard.check_if_key_in_dict("GdiffuseH", args)
        Guard.check_if_key_in_dict("surface", args)
        Guard.check_if_key_in_dict("Ta", args)
        Guard.check_if_key_in_dict("Tin", args)
        Guard.check_if_key_in_dict("Tout", args)

        self.args = args
        pass

    def calculate(self):
        """

        The returned object is of the form:
        {
            "usefulOutputPower":    [W]     (float)
            "IAMbeam":              [-]     (float between 0 and 1)
            "IAMdiffuse":           [-]     (float between 0 and 1)
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************

        latitude    [deg.]      Latitude, the angular location north or south of the equator, north positive
                                (float between -90 and 90)
        dayOfYear   [day]       Day of the year (integer between 1 and 365)
        solarTime   [hour]      Solar Time (float between 0 and 24)
        slope       [deg.]      Angle between the plane of the surface in question and the horizontal
                                (float between 0 and 180)
        orientation [deg.]      Surface orientation (surface azimuth angle), the deviation of the projection on a
                                horizontal plane of the normal to the surface from the local meridian, with zero due
                                south, east negative, and west positive; float between -180 and 180 (deg.).
        GbeamH      [W/m2]      Beam solar radiation onto a horizontal surface (positive float)
        GdiffuseH   [W/m2]      Diffuse solar radiation onto a horizontal surface (positive float)
        Ta          [deg.C]     Surrounding air temperature
        albedo      [-]         Ground albedo or ground reflection factor (strictly positive float)
        surface     [m2]        Surface of the solar collector (positive float)
        Tin         [deg.C]     Collector inlet temperature (float smaller than Tout)
        Tout        [deg.C]     Collector outlet temperature (float bigger than Tin)
        F           [-]         Zero loss efficiency (positive float)
        c1          [W/(m2*K)]  Heat loss coefficient at (Tm - Ta) = 0 (Tm = (Tin + Tout)/2) (positive float)
        c2          [W/(m2*K2)] Temperature dependence of the heat loss coefficient (positive float)


        *********************************************************************
        Outputs:
        *********************************************************************
        usefulOutputPower   [W]     Useful output power of solar collector
        IAMbeam             [-]     Incident Angle Modifier for beam radiance
        IAMdiffuse          [-]     Incident Angle Modifier for diffuse radiance


        *********************************************************************
        Notes:
        *********************************************************************

        This module calls three other modules:

            1.  "SolarFunctionIncidentAngle"
                in order to calculate incident angle of the beam onto the surface using latitude position, day of
                year, solar time,and slope and orientation of the surface

            2.  "SolarFunctionRadianceOntoTiltedPlane"
                in order to calculate direct and diffuse solar radiance onto the tilted surface with free orientation
                and slope from horizontal direct and diffuse radiance

            3.  "SolarThermal"
                in order to calculate useful output power of the flat plate solar collector (using outputs of the 2
                modules above)

            (specific documentations about used algorithms and references are available under these modules)

        """

        # Call SolarFunctionIncidentAngle function to calculate incidentAngle and zenithAngle
        incidentAngleArgs = {"latitude": float(self.args["latitude"]),
                             "dayOfYear": float(self.args["dayOfYear"]),
                             "solarTime": float(self.args["solarTime"]),
                             "slope": float(self.args["slope"]),
                             "orientation": float(self.args["orientation"])}
        incidentAngleOutput = SolarFunctionIncidentAngle(incidentAngleArgs).calculate()

        # Call SolarFunctionRadianceOntoTiltedPlane function to calculate beam and diffuse radiance onto tilted plane
        titledPlaneArgs = {"GbeamH": float(self.args["GbeamH"]),
                           "GdiffuseH": float(self.args["GdiffuseH"]),
                           "dayOfYear": float(self.args["dayOfYear"]),
                           "incidentAngle": float(incidentAngleOutput["incidentAngle"]),
                           "zenithAngle": float(incidentAngleOutput["zenithAngle"]),
                           "slope": float(self.args["slope"]),
                           "albedo": float(self.args["albedo"])}
        titledPlaneOutput = SolarFunctionRadianceOntoTiltedPlane(titledPlaneArgs).calculate()

        # Call SolarThermal to calculate useful output power of  the flat plate solar collector
        SolarThermalArgs = {"GbeamTiltedPlane": float(titledPlaneOutput["GbeamTiltedPlane"]),
                            "GdiffuseTiltedPlane": float(titledPlaneOutput["GdiffuseTiltedPlane"]),
                            "incidentAngle": float(incidentAngleOutput["incidentAngle"]),
                            "surface": float(self.args["surface"]),
                            "Ta": float(self.args["Ta"]),
                            "Tin": float(self.args["Tin"]),
                            "Tout": float(self.args["Tout"]),
                            "F": float(self.args["F"]),
                            "c1": float(self.args["c1"]),
                            "c2": float(self.args["c2"])}
        SolarThermalOutput = SolarThermal(SolarThermalArgs).calculate()

        return {
            "usefulOutputPower": SolarThermalOutput["usefulOutputPower"],
            "IAMbeam": SolarThermalOutput["IAMbeam"],
            "IAMdiffuse": SolarThermalOutput["IAMdiffuse"]
        }


    def get_reference(self):
        """
        get the scientific reference for this module
        """

        return conf.ref_thermal_solar_pv
