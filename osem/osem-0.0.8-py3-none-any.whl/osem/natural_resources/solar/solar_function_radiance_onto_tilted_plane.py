# coding=utf-8
from math import cos
from math import radians

from osem.general.enerapi.base.base import Base
from osem.general import conf
from osem.general.enerapi.common.Guard import *

__author__ = 'VincentRoch'


class SolarFunctionRadianceOntoTiltedPlane(Base):
    """
    Calculate direct and diffuse solar radiance onto a tilted plane with free orientation and slope from
    horizontal direct and diffuse radiance
    """

    _default_parameter_value = {
        "albedo": 0.2
    }

    @staticmethod
    def help():
        return SolarFunctionRadianceOntoTiltedPlane.__doc__ + "\r\n" + \
               SolarFunctionRadianceOntoTiltedPlane.calculate.__doc__

    @staticmethod
    def help_calculate():
        return SolarFunctionRadianceOntoTiltedPlane.__init__.__doc__.format(
            SolarFunctionRadianceOntoTiltedPlane._default_parameter_value["albedo"]
        )

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"GbeamH": 850.4, "GdiffuseH": 126.3, "dayOfYear": 158,
            "incidentAngle": 32.3, "zenithAngle": 23.6,
            "slope": 45.0, "albedo": 0.2}}

        {{
            GbeamH              [W/m2]      (positive float)
            GdiffuseH           [W/m2]      (positive float)
            dayOfYear           [day]       (integer between 1
                    and 365)
            incidentAngle       [deg.]      (0 smaller equal than
                    float smaller equal than 180)
            zenithAngle         [deg.]      (0 smaller equal than
                    float smaller equal than 180)
            slope               [deg.]      (0 smaller equal than
                    float smaller equal than 180)
            albedo              [-]         (0 smaller float)
                    default: {0},
        }}
        """

        super(SolarFunctionRadianceOntoTiltedPlane, self).__init__(args)

        Guard.check_if_key_in_dict("GbeamH", args)
        Guard.check_if_key_in_dict("GdiffuseH", args)
        Guard.check_if_key_in_dict("dayOfYear", args)
        Guard.check_if_key_in_dict("incidentAngle", args)
        Guard.check_if_key_in_dict("zenithAngle", args)
        Guard.check_if_key_in_dict("slope", args)

        Guard.check_is_higher(args["GbeamH"], lower_limit=0)
        Guard.check_is_higher(args["GdiffuseH"], lower_limit=0)
        Guard.check_is_higher(args["albedo"], lower_limit=0, strict=True)
        Guard.check_value_in_between(args["dayOfYear"], min=1, max=365)
        Guard.check_value_in_between(args["incidentAngle"], min=0, max=180)
        Guard.check_value_in_between(args["zenithAngle"], min=0, max=180)
        Guard.check_value_in_between(args["slope"], min=0, max=180)

        self.args = args
        pass

    def calculate(self):
        """

        The returned object is of the form:
        {
            "GbeamTiltedPlane":     [W/m2]  (0 smaller equal than float)
            "GdiffuseTiltedPlane":  [W/m2]  (0 smaller equal than float)
            "GtotalTiltedPlane":    [W/m2]  (0 smaller equal than float)
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        GbeamH          (Gbh)   [W/m2]      Beam solar radiation onto a horizontal surface
                                            (0 smaller equal than GbeamH)
        GdiffuseH       (Gdh)   [W/m2]      Diffuse solar radiation onto a horizontal surface
                                            (0 smaller equal than GdiffuseH)
        dayOfYear       (n)     [day]       Day of the year (1 smaller equal than dayOfYear smaller equal than 365)
        incidentAngle   (t)     [deg.]      Angle of incidence, the angle between the beam radiation on a surface and
                                            the normal to that surface (0 smaller equal than IncidentAngle
                                            smaller equal than 180)
        zenithAngle     (tz)    [deg.]      Angle between the vertical and the line to the sun, that is, the angle of
                                            incidence of beam radiation on a horizontal surface (cf. "Zenith angle"
                                            hereunder).(0 smaller equal than zenithAngle smaller equal than 180)
        slope           (b)     [deg.]      Angle between the plane of the surface in question and the horizontal;
                                            (0 smaller equal than slope smaller equal than 180).(slope bigger than 90
                                            means that the surface has  a downward-facing component.)
        albedo          (alb)   [-]         Ground albedo or ground reflection factor (0 smaller than albedo)


        *********************************************************************
        Outputs:
        *********************************************************************
        GbeamTiltedPlane    [W/m2]      Beam solar radiation onto a tilted surface of slope "slope"
                                        (0 smaller equal than GbeamTiltedPlane)
        GdiffuseTiltedPlane [W/m2]      Diffuse solar radiation onto a tilted surface of slope "slope"
                                        (0 smaller equal than GbeamTiltedPlane)
        GtotalTiltedPlane [W/m2]        Total solar radiation onto a tilted surface of slope "slope",
                                        GtotalTiltedPlane = GbeamTiltedPlane + GdiffuseTiltedPlane
                                        (0 smaller equal than GtotalTitledPlane)

        *********************************************************************
        Notes:
        *********************************************************************
        All calculations are taken from [1]
        The "_r" appended to variables means in Radians


        *********************************************************************
        Reference:
        *********************************************************************
        [1] B. Perers, P. Kovacs, M. Olsson, and M. P. U. Pettersson, "A Tool for Standardized Collector Performance
            Calculations including PVT" Energy Procedia, vol. 30, pp. 1354-1364, 2012.


        """
        n = self.args["dayOfYear"]
        Gbh = float(self.args["GbeamH"])
        Gdh = float(self.args["GdiffuseH"])
        b = float(self.args["slope"])
        alb = float(self.args["albedo"])
        t = float(self.args["incidentAngle"])
        tz = float(self.args["zenithAngle"])

        t_r = radians(t)
        tz_r = radians(tz)
        b_r = radians(b)

        # Conversion factor between the normal direction to the sun and the collector plane
        if t < 90 and tz < 90:
            Rb = cos(t_r)/cos(tz_r)  # [1]
        else:
            Rb = 0

        # Extraterrestrial solar radiation on horizontal surface
        Go = 1367 * (1 + 0.033 * cos(radians(360*n/365))) * cos(tz_r)  # [1]

        # Anisotropy index (how large fraction of the diffuse radiation that is circumsolar)
        Ai = Gbh/Go  # [1]

        # total solar radiation onto a horizontal surface
        Gth = Gbh + Gdh

        # The total radiation onto a tilted plane according to the Hay and Davies model
        Gtt = Gbh*Rb + Gdh*Ai*Rb + Gdh*(1-Ai)*0.5*(1+cos(b_r)) + Gth*alb*0.5*(1-cos(b_r))  # [1]

        Gbt = Gbh*Rb
        Gdt = Gtt - Gbt

        return {
            "GbeamTiltedPlane": Gbt,
            "GdiffuseTiltedPlane": Gdt,
            "GtotalTiltedPlane": Gtt
        }

    def get_reference(self):

        return conf.ref_solar_function_onto_tilted_plane
