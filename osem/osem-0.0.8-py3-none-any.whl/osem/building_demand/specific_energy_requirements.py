import json
from osem.general.enerapi.common.IoC import *
import os
from osem.general import conf
from osem.general.enerapi.base.base import Base
from osem.general.enerapi.common.Guard import *


class SpecificEnergyRequirements(Base):
    """
    Estimate specific energy needs (heating, hot water and electric) and equivalent hours of full charge for the
    building's heating system.
    """

    _default_parameter_value = {"refurbished": False, "standard": "SIA"}

    PERIODS = range(8011, 8024)  # needs to be improved
    BUILDING_USAGES = range(1, 13)  # needs to be improved
    CONSTRUCTION_STANDARDS = ["SIA", "Minergie", "MinergieP"]  # needs to be improved

    @staticmethod
    def help():
        return SpecificEnergyRequirements.__doc__ + "\r\n" + SpecificEnergyRequirements.calculate.__doc__

    @staticmethod
    def help_calculate():
        return SpecificEnergyRequirements.__init__.__doc__.format(
            ", ".join("{0}".format(n) for n in SpecificEnergyRequirements.PERIODS),
            ", ".join("{0}".format(n) for n in SpecificEnergyRequirements.BUILDING_USAGES),
            SpecificEnergyRequirements._default_parameter_value["refurbished"],
            ", ".join(SpecificEnergyRequirements.CONSTRUCTION_STANDARDS),
            SpecificEnergyRequirements._default_parameter_value["standard"])

    def __init__(self, args):
        """
        Arguments should be an object of the form:

        {{"affectation": 1, "period": 8020}}

        {{
            "affectation":  [int.]    (must be one of 1, 2, ..., 12)
            "period":       [int.]    (must be one of 8011, 8012, ..., 8023)

            "refurbished":  [bool.]   (true or false, default value: {2})
            "standard":     [str.]    (must be one of {3},
                default value: {4})
        }}
        """


        super(SpecificEnergyRequirements, self).__init__(args)

        self._data_folder_enerapi = conf.data_folder_enerapi
        self._file_per = conf.file_per
        self._file_affect = conf.file_affect
        self._file_ratio = conf.file_ratio


        with open(os.path.join(self._data_folder_enerapi, conf.file_per)) as data_file:
            periods  = json.load(data_file)
        with open(os.path.join(self._data_folder_enerapi, conf.file_affect)) as data_file:
            affects  = json.load(data_file)
        with open(os.path.join(self._data_folder_enerapi, conf.file_ratio)) as data_file:
            ratio_base  = json.load(data_file)

        if 'year' in args.keys():
            args["period"] = self._get_period_from_year(args['year'])

        period_list = []
        for key in periods.keys():
            period_list.append(periods[key]["GBAUP"])

        affect_list = []
        for key in affects.keys():
            affect_list.append(affects[key]["SIA_cat"])

        std_list = []
        for key in ratio_base["std_ratio"].keys():
            std_list.append(key)

        Guard.check_if_key_in_dict("affectation", args)
        Guard.check_if_key_in_dict("period", args)

        Guard.check_if_value_in_list(args["period"], values=period_list)
        Guard.check_if_value_in_list(args["affectation"], values=affect_list)
        Guard.check_if_value_in_list(args["standard"], values=std_list)
        Guard.check_if_value_in_list(args["refurbished"], values=[True, False])

        args["periods"] = periods
        args["affects"] = affects
        args["ratio_base"] = ratio_base

        self.args = args

    def calculate(self):
        """
        Perform the estimation for specific energy needs (heating, hot water and electricity) and equivalent hours of
        the building's heating system running at full charge.
        The returned object is of the form:

        ```
        {
            hS          [kWh/m2/year]
            hW          [kWh/m2/year]
            elec        [kWh/m2/year]
            h_full_ch   [h/year]
        }
        ```

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        affectation     [int.]          Building's affectation (SIA cat.)
        period          [int.]          Building's construction or refurbishment period (RegBL: GBAUP)
        refurbished     [bool.]         Set to True if the building have been refurbished (default value: True)
        standard        [str.]          Define the construction or refurbishment standard (default value: "SIA")

        *********************************************************************
        Outputs:
        *********************************************************************
        hS              [kWh/m2/year]   Specific heating needs
        hW              [kWh/m2/year]   Specific hot water needs
        elec            [kWh/m2/year]   Specific electricity needs (without heating)
        h_full_ch       [h/year]        Equivalent full charge functioning hours for a heat production plant

        Every estimation is based on parameters and coefficients find in [1] and [2].

        *********************************************************************
        Reference:
        *********************************************************************
        [1] Novatlantis. "Steps towards a sustainable development, a White Book for R&D of energy-efficient
        technologies". February 2004

        [2] L. Girardin. "A GIS-based Methodology for the Evaluation of Integrated Energy Systems in Urban Area".
        PhD thesis, STI, Lausanne, 2012

        """

        hs_ratio_aff = 0    # init
        hs_ratio_per = 0    # init
        hw_ratio = 0        # init
        elec_ratio = 0      # init
        h_full_ch = 0       # init

        for key in self.args["affects"]:
            if self.args["affects"][key]["SIA_cat"] == self.args["affectation"]:
                hs_ratio_aff = self.args["affects"][key]["hS_ratio"]
                hw_ratio = self.args["affects"][key]["hW_ratio"]
                elec_ratio = self.args["affects"][key]["elec_ratio"]
                h_full_ch = self.args["affects"][key]["h_full_ch"]

        for key in self.args["periods"]:
            if self.args["periods"][key]["GBAUP"] == self.args["period"]:
                hs_ratio_per = self.args["periods"][key]["hS_ratio"]

        ratio_std = self.args["ratio_base"]["std_ratio"][self.args["standard"]]

        hs = self.args["ratio_base"]["base_value"]["hS"] * hs_ratio_aff * hs_ratio_per * ratio_std
        hw = self.args["ratio_base"]["base_value"]["hW"] * hw_ratio
        elec = self.args["ratio_base"]["base_value"]["elec"] * elec_ratio

        if self.args["refurbished"] is True:
            hs = hs * self.args["ratio_base"]["refurbished_ratio"]

        return {
            "hS": round(hs, 2),
            "hW": round(hw, 2),
            "elec": round(elec, 2),
            "h_full_ch": h_full_ch
        }


    def get_reference(self):
        """
        return the reference for this module
        """
        return conf.ref_energy_requirement
