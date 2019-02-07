import json

from osem.general.enerapi.common.IoC import *
import os
from osem.general import conf
from osem.general.enerapi.base.base import Base
from osem.general.enerapi.common.Guard import *


class StaticHeatingCoolingPower(Base):
    """
    Estimate cooling and heating power based on Outdoor temperature, irradiance, period, affectation, building
    surfaces and volume, esa.
    """

    CONSTRUCTION_PERIODS = range(8011, 8024)  # needs to be improved
    BUILDING_USAGES = range(1, 13)  # needs to be improved

    @staticmethod
    def help():
        return StaticHeatingCoolingPower.__doc__ + "\r\n" + StaticHeatingCoolingPower.calculate.__doc__

    @staticmethod
    def help_calculate():
        return StaticHeatingCoolingPower.__init__.__doc__.format(
                ", ".join("{0}".format(n) for n in StaticHeatingCoolingPower.BUILDING_USAGES),
                ", ".join("{0}".format(n) for n in StaticHeatingCoolingPower.CONSTRUCTION_PERIODS))

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"period": 8011, "affectation": 2, "sre": 200, "s_wall": 255,
            "s_window": 45, "s_roof": 100, "s_floor": 100, "esa": 45,
            "t_ext": [32, 33], "irr_south": [700, 720]}}

        {{
            "affectation":  [int.]
                (must be one of 1, 2, ..., 12)
            "period":       [int.]
                (must be one of 8011, 8012, ..., 8023)
            "sre":          [m2]
                (must be a positive float)
            "s_wall":       [m2]
                (must be a positive float)
            "s_window":     [m2]
                (must be a positive float)
            "s_roof":       [m2]
                (must be a positive float)
            "s_floor":      [m2]
                (must be a positive float)
            "esa":          [m2]
                (must be a positive float)
            "t_ext":        [deg. C] (list)
                (must be between -30 and 45)
            "irr_south":    [W/m2] (list)
                (must be a positive integer)
        }}
        """

        super(StaticHeatingCoolingPower, self).__init__(args)


        self._data_folder_enerapi = conf.data_folder_enerapi




        with open(os.path.join(self._data_folder_enerapi, conf.file_construct_bat)) as data_file:
            construct_bat  = json.load(data_file)

        with open(os.path.join(self._data_folder_enerapi, conf.file_sia_380_1)) as data_file:
            sia_ref  = json.load(data_file)



        Guard.check_if_key_in_dict("affectation", args)
        Guard.check_if_key_in_dict("period", args)
        Guard.check_if_key_in_dict("sre", args)
        Guard.check_if_key_in_dict("s_wall", args)
        Guard.check_if_key_in_dict("s_window", args)
        Guard.check_if_key_in_dict("s_roof", args)
        Guard.check_if_key_in_dict("s_floor", args)
        Guard.check_if_key_in_dict("esa", args)
        Guard.check_if_key_in_dict("t_ext", args)
        Guard.check_if_key_in_dict("irr_south", args)

        Guard.check_is_higher(args["sre"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["s_wall"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["s_window"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["s_roof"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["s_floor"], lower_limit=0, strict=True)
        Guard.check_is_higher(args["esa"], lower_limit=0, strict=True)

        Guard.check_if_value_in_list(args["affectation"], values=StaticHeatingCoolingPower.BUILDING_USAGES)
        Guard.check_if_value_in_list(args["period"], values=StaticHeatingCoolingPower.CONSTRUCTION_PERIODS)

        Guard.check_for_every_item_of_list(args["t_ext"], Guard.check_value_in_between, min=-30, max=45)
        Guard.check_for_every_item_of_list(args["irr_south"], Guard.check_is_higher, lower_limit=0)

        Guard.check_for_same_list_lengths(t_ext=args["t_ext"], irr_south=args["irr_south"])

        args["construct_bat"] = construct_bat
        args["sia_ref"] = sia_ref

        self.args = args
        pass

    def calculate(self):
        """
        Estimate cooling and heating power based on Outdoor temperature, irradiance, period, affectation, building
        surfaces and volume, esa.

        The returned object is of the form:
        {
            "Penvelope_heating":    [Watt] (list)
            "Penvelope_cooling":    [Watt] (list)
            "Psol":                 [Watt] (list)
            "Pocc":                 [Watt] (list)
            "Ptot_heating":         [Watt] (list)
            "Ptot_cooling":         [Watt] (list)
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        period              [int.]              period from RegBL
        affectation         [int.]              SIA category
        sre                 [m2]                Building heated area
        s_wall              [m2]                Wall surfaces
        s_window            [m2]                Window surfaces
        s_roof              [m2]                Roof surfaces
        s_floor             [m2]                Floor surfaces
        esa                 [m2]                Equivalent South Area
        t_ext               [deg. C] (list)     Outdoor Temperature
        irr_south           [W/m2]   (list)     Solar irradiance

        *********************************************************************
        Outputs:
        *********************************************************************
        Penvelope_heating   [Watt] (list)       Thermal power gains through the building envelope (with heating temperature set)
        Penvelope_cooling   [Watt] (list)       Thermal power gains through the building envelope (with cooling temperature set)
        Psol                [Watt] (list)       Thermal power gains from solar energy
        Pocc                [Watt] (list)       Thermal power gains through occupants
        Ptot_heating        [Watt] (list)       Total thermal power gains (with heating temperature set)
        Ptot_cooling        [Watt] (list)       Total thermal power gains (with cooling temperature set)

        U coefficients are based on annexes of the thesis [1].

        Thermal Bridges values on [2].

        Internal gains linked with occupancy based on the annexes of the SIA 380/1.

        *********************************************************************
        Reference:
        *********************************************************************
        [1]D. Perez. "A framework to model and simulate the disaggregated energy flows supplying buildings in urban
        areas". PhD thesis, LESO-PB EPFL, Lausanne, 2014

        [2]"Catalogue des ponts thermiques", OFEN : document describing basic thermal bridges knowing building
        construction method

        """

        period = self.args["period"]
        affectation = self.args["affectation"]
        sre = self.args["sre"]
        s_wall = self.args["s_wall"]
        s_window = self.args["s_window"]
        s_roof = self.args["s_roof"]
        s_floor = self.args["s_floor"]
        esa = self.args["esa"]

        t_cool_set_point = 0
        t_heat_set_point = 0
        surf_pers = 0
        heat_pers = 0
        u_roof = 0
        u_wall = 0
        u_floor = 0
        u_window = 0
        g = 0

        for affect in self.args["sia_ref"]["data"]:
            if affectation == self.args["sia_ref"]["data"][affect]["SIA_cat"]:
                t_cool_set_point = self.args["sia_ref"]["data"][affect]["t_cool_set_point"]
                t_heat_set_point = self.args["sia_ref"]["data"][affect]["t_heat_set_point"]
                surf_pers = self.args["sia_ref"]["data"][affect]["surf_pers"]
                heat_pers = self.args["sia_ref"]["data"][affect]["heat_pers"]

        for affect in self.args["construct_bat"]["data"]:
            if affectation == self.args["construct_bat"]["data"][affect]["SIA_cat"]:
                for per in self.args["construct_bat"]["data"][affect]:
                    if per == "SIA_cat":
                        pass

                    else:
                        if period == self.args["construct_bat"]["data"][affect][per]["GBAUP"]:
                            u_roof = self.args["construct_bat"]["data"][affect][per]["Uroof"]
                            u_wall = self.args["construct_bat"]["data"][affect][per]["Uwall"]
                            u_floor = self.args["construct_bat"]["data"][affect][per]["Ufloor"]
                            u_window = self.args["construct_bat"]["data"][affect][per]["Uwindow"]
                            g = self.args["construct_bat"]["data"][affect][per]["g"]

        pEnvCool = []
        pEnvHeat = []
        pSol = []
        pOcc = []
        pTotCool = []
        pTotHeat = []

        for t, irr in zip(self.args["t_ext"], self.args["irr_south"]):
            p_envelope_cool = (s_wall * u_wall + s_window * u_window + s_roof * u_roof + s_floor * u_floor) * (
                t - t_cool_set_point)
            p_envelope_heat = (s_wall * u_wall + s_window * u_window + s_roof * u_roof + s_floor * u_floor) * (
                t - t_heat_set_point)

            p_sol = esa * irr * g
            p_occ = float(sre) / float(surf_pers) * float(heat_pers)

            p_tot_cool = max(p_envelope_cool + p_sol + p_occ, 0)
            p_tot_heat = abs(min(p_envelope_heat + p_sol + p_occ, 0))

            pEnvCool.append(p_envelope_cool)
            pEnvHeat.append(p_envelope_heat)
            pSol.append(p_sol)
            pOcc.append(p_occ)
            pTotCool.append(p_tot_cool)
            pTotHeat.append(p_tot_heat)

        return {
            "Penvelope_heating": pEnvHeat,
            "Penvelope_cooling": pEnvCool,
            "Psol": pSol,
            "Pocc": pOcc,
            "Ptot_heating": pTotHeat,
            "Ptot_cooling": pTotCool
        }

    def get_reference(self):
        """
        return the reference
        """
        return conf.ref_static_heating_cooling_power
