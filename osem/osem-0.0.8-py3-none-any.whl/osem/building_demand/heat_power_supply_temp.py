import json
from pprint import pprint
import os
from osem.general import conf
from osem.general.enerapi.base.base import Base
from .specific_energy_requirements import SpecificEnergyRequirements
from osem.general.enerapi.common.Guard import *


class HeatPowerSupplyTemp(Base):
    """
    Estimate heating power and heating supply and return temperatures for a building based on the external temperature.
    """

    _default_parameter_value = {"refurbished": False, "standard": "SIA", "t_dim": -10, "t_max_heat": 15}

    CONSTRUCTION_PERIODS = range(8011, 8024)
    BUILDING_USAGES = range(1, 13)
    CONSTRUCTION_STANDARDS = ["SIA", "Minergie", "MinergieP"]
    ENERGY_SOURCES = range(7200, 7210)

    @staticmethod
    def help():
        return HeatPowerSupplyTemp.__doc__ + "\r\n" + HeatPowerSupplyTemp.calculate.__doc__

    @staticmethod
    def help_calculate():
        return HeatPowerSupplyTemp.__init__.__doc__.format(
            ", ".join("{0}".format(n) for n in HeatPowerSupplyTemp.BUILDING_USAGES),
            ", ".join("{0}".format(n) for n in HeatPowerSupplyTemp.CONSTRUCTION_PERIODS),
            HeatPowerSupplyTemp._default_parameter_value["refurbished"],
            ", ".join(HeatPowerSupplyTemp.CONSTRUCTION_STANDARDS),
            HeatPowerSupplyTemp._default_parameter_value["standard"],
            ", ".join("{0}".format(n) for n in HeatPowerSupplyTemp.ENERGY_SOURCES),
            HeatPowerSupplyTemp._default_parameter_value["t_dim"],
            HeatPowerSupplyTemp._default_parameter_value["t_max_heat"])

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"affectation": 1, "period": 8020, "SRE": 100, "ae": 7201, "t_ext": [0]}}

        {{
            "affectation":  [int.]
                (must be one of {0})
            "period":       [int.]
                (must be one of 8011, 8012, ..., 8023)
            "SRE":          [m2]
                (must be a strictly positive integer)
            "t_ext"         [deg.]  (list)
                (must be between -30 deg. and 50 deg.)
            "ae"            [int.]
                (must be one of 7200, 7201, ... 7209)

            "refurbished":  [bool.]
                (true or false, default value: {2})
            "standard":     [str.]
                (must be one of {3}, default value: {4})
            "dh_max":       [deg.]
                (must be strictly positive, no default value)
            "t_dim":        [deg.]
                (default value: {6})
            "t_max_heat":   [deg.]
                (default value: {7})
        }}
        """
        super(HeatPowerSupplyTemp, self).__init__(args)

        self._data_folder_enerapi = conf.data_folder_enerapi
        self._file_sia_380_1 = conf.file_sia_380_1
        self._file_em_system = conf.file_em_system
        with open(os.path.join(self._data_folder_enerapi, self._file_sia_380_1)) as data_file:
            data_sia  = json.load(data_file)
        with open(os.path.join(self._data_folder_enerapi, self._file_em_system)) as data_file:
            data_em_sys  = json.load(data_file)





        Guard.check_if_key_in_dict("affectation", args)
        Guard.check_if_key_in_dict("period", args)
        Guard.check_if_key_in_dict("SRE", args)
        Guard.check_if_key_in_dict("t_ext", args)
        Guard.check_if_key_in_dict("ae", args)

        Guard.check_if_value_in_list(args["period"], values=HeatPowerSupplyTemp.CONSTRUCTION_PERIODS)
        Guard.check_if_value_in_list(args["affectation"], values=HeatPowerSupplyTemp.BUILDING_USAGES)
        Guard.check_if_value_in_list(args["standard"], values=HeatPowerSupplyTemp.CONSTRUCTION_STANDARDS)
        Guard.check_if_value_in_list(args["ae"], values=HeatPowerSupplyTemp.ENERGY_SOURCES)
        Guard.check_if_value_in_list(args["refurbished"], values=[True, False])

        Guard.check_is_higher(args["SRE"], lower_limit=0, strict=True)
        Guard.check_for_every_item_of_list(args["t_ext"], Guard.check_value_in_between, min=-30, max=50)

        Guard.check_is_higher(args["t_max_heat"], lower_limit=args["t_dim"], strict=True)

        if "dh_max" in args.keys():
            Guard.check_is_higher(args["dh_max"], lower_limit=0, strict=True)

        args["data_SIA"] = data_sia
        args["data_em_sys"] = data_em_sys

        self.args = args

    def calculate(self):
        """
        Estimate heating power and heating supply and return temperatures.
        The returned object is of the form:

        ```
        {
            p_heating       [kW]    (list)
            t_supply        [deg]   (list)
            t_return        [deg]   (list)
            p_installed     [kW]
        }
        ```

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        affectation     [int.]          Building's affectation (SIA cat.)
        period          [int.]          Building's construction or refurbishment period (RegBL: GBAUP)
        refurbished     [bool.]         Set to True if the building have been refurbished (default value: False)
        standard        [str.]          Define the construction or refurbishment standard (default value: "SIA")
        SRE             [m2]            Building's energy reference surface
        ae              [int.]          Building's energy source
        t_ext           [deg.]  (list)  External temperature for considered time step(s)
        dh_max          [deg.h]         Maximum Dh for the localisation
        t_dim           [deg.]          Design minimal external temperature (default value: -10)
        t_max_heat      [deg.]          Maximal heating external temperature (default value: 15)

        *********************************************************************
        Outputs:
        *********************************************************************
        p_heating       [kW]    (list)  Heating power
        t_supply        [deg]   (list)  Heating supply temperature
        t_return        [deg]   (list)  Heating return temperature
        p_installed     [kW]            Installed heating power

        *********************************************************************
        Reference:
        *********************************************************************
        Methods are currently (2015) unpublished and will soon be fully tested and compared to existing equivalent
        methods.

        """

        t_dim = self.args["t_dim"]
        t_max_heat = self.args["t_max_heat"]

        t_set = 0  # init
        niv_t_sup = 0  # init
        niv_t_ret = 0  # init

        for key in self.args["data_SIA"]["data"]:
            if self.args["data_SIA"]["data"][key]["SIA_cat"] == self.args["affectation"]:
                t_set = self.args["data_SIA"]["data"][key]["t_heat_set_point"]

        def identify_return_temperature(supply_temp):
            supply_temperatures = [70, 60, 55, 40, 35]
            return_temperatures = [50, 45, 40, 30, 25]
            if supply_temp in supply_temperatures:
                idx = supply_temperatures.index(supply_temp)
                return return_temperatures[idx]
            else:
                return supply_temp - 15

        def extrapolate_temperature(temperature, niv_t):
            return float(t_max_heat - temperature) / (t_max_heat - t_dim) * (niv_t - t_set) + t_set

        for period in self.args["data_em_sys"]["data"]:
            for ae in self.args["data_em_sys"]["data"][period]:
                if not ae == "GBAUP":
                    if self.args["data_em_sys"]["data"][period][ae]["GENHZ-WW"] == self.args["ae"]:
                        niv_t_sup = self.args["data_em_sys"]["data"][period][ae]["niv_t"]
                        niv_t_ret = identify_return_temperature(niv_t_sup)

        if "dh_max" in self.args.keys():
            dh_max = float(self.args["dh_max"])
        else:
            dh_max = float(t_set - t_dim)

        args = {"affectation": self.args["affectation"],
                "period": self.args["period"],
                "refurbished": self.args["refurbished"],
                "standard": self.args["standard"]}

        prim_results = SpecificEnergyRequirements(args).calculate()

        h_full_ch = prim_results["h_full_ch"]
        hs = prim_results["hS"]
        needs_hs_tot = hs * self.args["SRE"]
        p_nom = needs_hs_tot / h_full_ch

        p_heat = []
        t_sup = []
        t_ret = []

        for t in self.args["t_ext"]:

            if t < t_max_heat:
                p_heat.append(round(((t_set - t) / dh_max) * p_nom, 2))
                t_sup.append(round(extrapolate_temperature(t, niv_t_sup), 1))
                t_ret.append(round(extrapolate_temperature(t, niv_t_ret), 1))

            else:
                p_heat.append(0)
                t_sup.append(0)
                t_ret.append(0)

        return {
            "p_heating": p_heat,
            "t_supply": t_sup,
            "t_return": t_ret,
            "p_installed": round(p_nom, 1)
        }

    def get_reference(self):
        """
        return the reference for this module. In this particularcase, no reference is present as the method
        was developed internally.
        """

        return None
