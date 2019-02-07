import json

from osem.general.enerapi.common.IoC import *
import os
from osem.general import conf
from osem.general.enerapi.base.base import Base
from osem.general.enerapi.common.Guard import *


class MaximumLegalHeatingDemand(Base):
    """
    Based on the Swiss norm 380/1, calculate the limit for the thermal heating energy in buildings (Qhli), based on
    heated floor area, thermal envelope surface, weather station and the nature of the project (new building,
    extension, new affectation, refurbishment)
    """

    project_ids = range(1, 5)
    category_ids = range(1, 13)
    weather_ids = range(1, 9)

    @staticmethod
    def help():
        return MaximumLegalHeatingDemand.__doc__ + "\r\n" \
               + MaximumLegalHeatingDemand.calculate.__doc__

    @staticmethod
    def help_calculate():
        return MaximumLegalHeatingDemand.__init__.__doc__.format(
            ", ".join("{0}".format(n) for n in MaximumLegalHeatingDemand.project_ids),
            ", ".join("{0}".format(n) for n in MaximumLegalHeatingDemand.category_ids),
            ", ".join("{0}".format(n) for n in MaximumLegalHeatingDemand.weather_ids),
        )

    def __init__(self, args):
        """

        Arguments should be an object of the form:

        {{"Ath": 450, "Ae": 150, "Affect": 1, "Weather_Station": 5,
        "project_nature": 4}}

        {{
            "Ath":               [int.]    (must be a positive integer)
            "Ae":                [int.]    (must be a positive integer)
            "Affect":            [int.]    (must be one of 1, 2, ..., 12)
            "Weather_Station":   [int.]    (must be one of 1, 2, ..., 8)
            "project_nature":    [int.]    (must be one of {0})
        }}

        """

        super(MaximumLegalHeatingDemand, self).__init__(args)

        self._data_folder_enerapi = conf.data_folder_enerapi


        with open(os.path.join(self._data_folder_enerapi, conf.file_project_nature)) as data_file:
            project_nature_dict  = json.load(data_file)
        with open(os.path.join(self._data_folder_enerapi, conf.file_data_qhli)) as data_file:
            data_qhli_dict  = json.load(data_file)
        with open(os.path.join(self._data_folder_enerapi, conf.file_meteo_2028)) as data_file:
            meteo_dict  = json.load(data_file)


        Guard.check_if_key_in_dict("Ath", args)
        Guard.check_if_key_in_dict("Ae", args)
        Guard.check_if_key_in_dict("Affect", args)
        Guard.check_if_key_in_dict("Weather_Station", args)
        Guard.check_if_key_in_dict("project_nature", args)

        Guard.check_is_higher(args["Ath"], strict=True, lower_limit=0)
        Guard.check_is_higher(args["Ae"], strict=True, lower_limit=0)

        Guard.check_value_in_between(args["project_nature"], min=1, max=5)
        Guard.check_value_in_between(args["Affect"], min=1, max=13)
        Guard.check_value_in_between(args["Weather_Station"], min=1, max=9)

        args["project_nature_dict"] = project_nature_dict
        args["data_qhli_dict"] = data_qhli_dict
        args["meteo_dict"] = meteo_dict
        self.args = args

    def calculate(self):
        """
        Calculate the limit value for the heating thermal energy in buildings (Qhli), based on heated floor area,
        thermal envelope surface, weather station and the nature of the project (new building, extension,
        new affectation, refurbishment)
        The returned object is of the form:

        {
            "Qhli":         [MJ/m2]
        }

        Detailed Description:

        *********************************************************************
        Inputs:
        *********************************************************************
        Ath                  [m2]      thermal envelope surface
        Ae                   [m2]      heated floor area
        Affect               [int.]    SIA Category; logement_Collectif: 1, Maison_Individuelle : 2,
                                       Administration: 3, Ecoles: 4, Commerces: 5, Restaurant: 6,
                                       Lieux_de_Rassemblement: 7, Hopitaux: 8, Industries: 9,Depots: 10,
                                       Instal._Sportives: 11, Piscines_Couv: 12
        Weather_Station      [int.]    weather station; Pully: 1, Payerne: 2, La Fretaz: 3, Aigle: 4, Sion: 5,
                                       Montana : 6, Zermatt: 7, Grand-St-Bernard: 8
        project_nature       [int.]    nature of the construction project; New_building: 1, Extension: 2,
                                       New_affectation: 3, Refurbishment: 4

        *********************************************************************
        Outputs:
        *********************************************************************
        Qhli         [MJ/m2]            limit for heating thermal energy in buildings
        kWh_per_m2   [kWh/m2]           limit for heating thermal energy in buildings

        The calculation method is based on SIA 380/1 [1]

        *********************************************************************
        Reference:
        *********************************************************************
        [1] SIA 380/1 Norm, heating thermal energy in buildings, edition 2009

        """
        affectation = self.args["Affect"]
        project_nature = self.args["project_nature"]
        weather_station = self.args["Weather_Station"]
        ath = self.args["Ath"]
        ae = self.args["Ae"]
        text_moy = 0
        qhli0 = 0
        dqhli = 0
        coef_nature = 0

        for station in self.args["meteo_dict"]["data"]:
            if weather_station == self.args["meteo_dict"]["data"][station]["Weather_Station_ref"]:
                text_moy = self.args["meteo_dict"]["data"][station]["Text_Moy"]

        for affect in self.args["data_qhli_dict"]["data"]:
            if affectation == self.args["data_qhli_dict"]["data"][affect]["SIA_cat"]:
                qhli0 = self.args["data_qhli_dict"]["data"][affect]["Qhli0"]
                dqhli = self.args["data_qhli_dict"]["data"][affect]["DQhli"]

        for project in self.args["project_nature_dict"]["data"]:
            if project_nature == self.args["project_nature_dict"]["data"][project]["project_nature"]:
                coef_nature = self.args["project_nature_dict"]["data"][project]["Coef_nature"]

        qhli_initial = (qhli0 + dqhli * float(ath) / ae) * (1 - (text_moy - 8.5) * 0.08)
        correct_qhli = float(qhli_initial * coef_nature)

        return {
            'Qhli': correct_qhli, 'kWh_per_m2': correct_qhli / 3.6
        }

    def get_reference(self):

        return conf.ref_maximum_legal_heating_demand