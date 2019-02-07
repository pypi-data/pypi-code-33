# coding=utf-8
from math import acos
from math import atan
from math import cos
from math import degrees
from math import pi
from math import radians
from math import sin
from math import tan

from osem.general.enerapi.base.base import Base
from osem.general import conf
from osem.general.enerapi.common.Guard import *


class SolarFunctionIncidentAngle(Base):
    """
    Calculate solar position (zenith angle and solar azimuth angle), as well as incident angle, longitudinal and
    transversal incident angles (for a definite surface) of solar beams from latitude position, day of year, solar time,
    slope and azimuth of a surface
    """

    @staticmethod
    def help():
        return SolarFunctionIncidentAngle.__doc__ + \
               "\r\n" + SolarFunctionIncidentAngle.calculate.__doc__

    @staticmethod
    def help_calculate():
        return SolarFunctionIncidentAngle.__init__.__doc__.format()

    def __init__(self, args):
        """

        Arguments should be an object of the form:

        {{"latitude": 46.100458, "dayOfYear": 235, "solarTime": 13.77,
        "slope": 35.0, "orientation": 45.0}}

        {{
            latitude        [deg.]      (float between -90 and 90)
            dayOfYear       [day]       (int between 1 and 365)
            solarTime       [hour]      (float between 0 and smaller than 24)
            slope           [deg.]      (float between 0 and 180)
            orientation     [deg.]      (float between -180 and 180)
        }}


        """

        super(SolarFunctionIncidentAngle, self).__init__(args)

        Guard.check_if_key_in_dict("latitude", args)
        Guard.check_if_key_in_dict("dayOfYear", args)
        Guard.check_if_key_in_dict("solarTime", args)
        Guard.check_if_key_in_dict("slope", args)
        Guard.check_if_key_in_dict("orientation", args)

        Guard.check_value_in_between(args["latitude"], min=-90, max=90)
        Guard.check_value_in_between(args["dayOfYear"], min=1, max=365)
        Guard.check_value_in_between(args["solarTime"], min=0, max=24, max_in=False)
        Guard.check_value_in_between(args["slope"], min=0, max=180)
        Guard.check_value_in_between(args["orientation"], min=-180, max=180)

        self.args = args
        pass

    def calculate(self):
        """

        The returned object is of the form:

        {
            "zenithAngle":          [deg.]  (float between 0 and 180)
            "solarAzimuthAngle":    [deg.]  (float between -180 and 180)
            "incidentAngle":        [deg.]  (float between 0 and 180)
            "longIncidentAngle":    [deg.]  (float between -90 and 90)
            "tranIncidentAngle":    [deg.]  (float between -90 and 90)
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************

        latitude        [deg.]  (float between -90 and 90)    Position cf. Phi (hereunder)
        dayOfYear       [day]   (int between 1 and 365)       Day of the year
        solarTime       [hour]  (float between 0 and 24)      Solar Time
        slope           [deg.]  (float between 0 and 180)     cf. Beta (hereunder)
        orientation     [deg.]  (float between -180 and 180)  cf. Gamma (hereunder)


        *********************************************************************
        Outputs:
        *********************************************************************
        zenithAngle         [deg.]  Angle between the vertical and the line to the sun, that is, the angle of incidence
                                    of beam radiation on a horizontal surface (cf. "Zenith angle" hereunder).
                                    (0 smaller equal than zenithAngle smaller equal than 180)
        solarAzimuthAngle   [deg.]  Angular displacement from south of the projection of beam radiation on the
                                    horizontal plane. Displacements east of south are negative and west of south are
                                    positive. (cf. "Solar azimuth angle hereunder")
                                    (-180 smaller equal than solarAzimuthAngle smaller equal than 180)
        incidentAngle       [deg.]  Angle of incidence, the angle between the beam radiation on a surface and the
                                    normal to that surface. (cf. "Theta" hereunder)
                                    (0 smaller equal than incidentAngle smaller equal than 180)
        longIncidentAngle   [deg.]  Longitudinal North-South incident angles (bigger 0 means to the
                                    "north" of collector* normal)
                                    (-90 smaller equal than longIncidentAngle smaller equal than 90)
        tranIncidentAngle   [deg.]  Transversal East-West incident angles
                                    (bigger 0 means to the "west" of collector normal)
                                    (-90 smaller equal than tranIncidentAngle smaller equal than 90)


        *********************************************************************
        Variables description (taken from [1]):
        *********************************************************************
        Phi     (p) [deg.]  Latitude, the angular location north or south of the equator, north positive;
                            -90 smaller equal than p smaller equal than 90
        Delta   (d) [deg.]  Declination, the angular position of the sun at solar noon (i.e., when the sun is on the
                            local meridian) with respect to the plane of the equator, north positive;
                            -23.45 smaller equal to d smaller equal to 23.45.
        Beta    (b) [deg.]  Slope, the angle between the plane of the surface in question and the horizontal;
                            0 smaller equal to b smaller to 180.(b bigger than 90 (deg.) means that the surface has a
                            downward-facing component.)
        Gamma   (g) [deg.]  Surface orientation (surface azimuth angle), the deviation of the projection on a horizontal
                            plane of the normal to the surface from the local meridian, with zero due south, east
                            negative, and west positive; -180 smaller equal to g smaller equal to 180 (deg.).
        Omega   (o) [deg.]  Hour angle, the angular displacement of the sun east or west of the local meridian due to
                            rotation of the earth on its axis at 15 (deg.) per hour; morning negative, afternoon
                            positive.
        Theta   (t) [deg.]  Angle of incidence, the angle between the beam radiation on a surface and the normal to that
                            surface.


        *********************************************************************
        Additional angles are defined that describe the position of the sun in the sky:
        *********************************************************************
        Zenith angle            (tz)    [deg.]  the angle between the vertical and the line to the sun, that is, the
                                                angle of incidence of beam radiation on a horizontal surface.
        Solar azimuth angle     (gs)    [deg.]  the angular displacement from south of the projection of beam radiation
                                                on the horizontal plane. Displacements east of south are negative and
                                                west of south are positive.


        *********************************************************************
        Notes:
        *********************************************************************
        The "_r" appended to variables means in Radians

        Only valid for northern hemisphere


        *********************************************************************
        Reference:
        *********************************************************************
        [1] Duffie,J.A. and Beckman W.A. Solar Engineering of Thermal Processes (4th edition), chapter 1.6
        [2] B. Perers, P. Kovacs, M. Olsson, and M. P. U. Pettersson, "A Tool for Standardized Collector Performance
            Calculations including PVT" Energy Procedia, vol. 30, pp. 1354-1364, 2012.

        """

        p = float(self.args["latitude"])  # Phi
        n = self.args["dayOfYear"]
        o = 15 * (float(self.args["solarTime"])-12)  # Omega
        b = float(self.args["slope"])  # Beta
        g = float(self.args["orientation"])  # Gamma
        B = (n-1)*360.0/365.0  # [1]
        d = (180.0/pi) * (0.006918 - 0.399912*cos(radians(B)) + 0.070257*sin(radians(B)) -
                          0.006758*cos(radians(2*B)) + 0.000907*sin(radians(2*B)) - 0.002697*cos(radians(3*B)) +
                          0.00148*sin(radians(3*B)))  # [1] Delta
        p_r = radians(p)
        o_r = radians(o)
        b_r = radians(b)
        g_r = radians(g)
        d_r = radians(d)

        t_r = acos(sin(d_r)*sin(p_r)*cos(b_r) - sin(d_r)*cos(p_r)*sin(b_r)*cos(g_r) +
                   cos(d_r)*cos(p_r)*cos(b_r)*cos(o_r) + cos(d_r)*sin(p_r)*sin(b_r)*cos(g_r)*cos(o_r) +
                   cos(d_r)*sin(b_r)*sin(g_r)*sin(o_r))  # [1] Theta
        t = degrees(t_r)

        tz_r = acos(cos(p_r)*cos(d_r)*cos(o_r) + sin(p_r)*sin(d_r))  # [1] Zenith angle
        tz = degrees(tz_r)

        # [1] Solar azimuth angle
        if o < 0:
            gs_r = -acos(round((cos(tz_r)*sin(p_r)-sin(d_r)), 10)/round((sin(tz_r)*cos(p_r)), 10))
            gs = degrees(gs_r)
        else:
            gs_r = acos(round((cos(tz_r)*sin(p_r)-sin(d_r)), 10)/round((sin(tz_r)*cos(p_r)), 10))
            gs = degrees(gs_r)

        # calculation of longitudinal North-South (tLon) and transversal East-West (tTra) incident angles
        if tz < 90 and t < 90:
            tTra_r = atan(sin(tz_r)*sin(gs_r-g_r)/cos(t_r))  # [2]
            tTra = degrees(tTra_r)

            tLon_r = -(atan(tan(tz_r)*cos(gs_r-g_r))-b_r)  # [2]
            tLon = degrees(tLon_r)
        else:
            tTra = 90
            tLon = 90


        return {
            "zenithAngle": tz,
            "solarAzimuthAngle": gs,
            "incidentAngle": t,
            "longIncidentAngle": tLon,
            "tranIncidentAngle": tTra
        }

    def get_reference(self):

        return conf.ref_solar_function_incident_angle