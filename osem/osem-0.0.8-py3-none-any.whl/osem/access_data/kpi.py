import pandas as pd
import numpy as np
import os

import osem.general.conf as conf
from osem.access_data.kbob import Kbob
from osem.access_data.price import Price
from osem.general.helper import find_string

class Kpi:
    """
    Ths class compute different kpi
    """

    def __init__(self):

        # link to external data
        self._data_folder = conf.data_folder
        self._kbob = Kbob()
        self._price = Price()

        # efficiency
        self._filename_eff = conf.filename_eff
        self._data_efficiency = self._load_efficiency_data()
        self._cutoff = conf.cutoff
        self.zero_abs = 273.15

        # heating temperature of buildings
        self.temp_building = conf.temp_building  # might be more than one temperature
        self._temp_ext = conf.temp_ext

        # kpi based on the price database
        self.kpi_from_price = [i.lower() for i in conf.kpi_from_price]

    def _load_efficiency_data(self):
        """
        This function load the efficiency data
        """

        filename_eff = os.path.join(self._data_folder, self._filename_eff)
        data_efficiency = pd.read_csv(filename_eff, index_col=0, sep=';')

        return data_efficiency

    def get_co2_emission(self, data_heating):
        """
        This function compute c02 emission of different heating technology based on useful energy
        :param data_heating: A dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
        :return: a Dataframe with the c02 emission by technology by year by scenarios in kg
        """

        # compute co2
        co2_emi = _create_empty_output(data_heating)
        for tech_name in co2_emi.columns[2:]:
            co2_rate = self._kbob.get_value(tech_name, 'CO2', language="ENG", ener_type='useful')
            co2_emi[tech_name] = co2_rate * data_heating[tech_name]

        return co2_emi

    def get_renewable_part(self, data_heating):
        """
        The function computes the part of renewable energy from different technology based on useful energy.
        :param data_heating: A dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
        :return: a Dataframe with the renewable energy by technology by year by scenarios in kWh
        """

        # create the output dataframe
        renewable =  _create_empty_output(data_heating)
        # compute renewable
        for tech_name in renewable.columns[2:]:
            renew_coeff = self._kbob.get_value(tech_name, 'EP_Renew', language="ENG", ener_type='useful')
            renewable[tech_name] = renew_coeff * data_heating[tech_name]

        return renewable

    def get_energy_final(self, data_heating, temp_building=None):
        """
        This function return the final energy from the useful energy. For an heat pump, the efficiency accounts
         for the building temperature through Carnot.
        :param data_heating: A dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
        :param temp_build: the temperature of the buildings in the form
               [[Percent building1, Percent building2,...], [T1, T2,...]] in Celsius.
        :return: a dataframe with the final energy
        """
        # temperature of the building
        if temp_building is not None:
            self.temp_building = temp_building
        self.temp_building = np.array(self.temp_building)


        # create the output dataframe
        final_energy = _create_empty_output(data_heating)

        # compute final energy
        for tech_name0 in data_heating.columns[2:]:
            # get correct name
            tech_name = find_string(tech_name0, self._data_efficiency.index, cutoff=self._cutoff)

            # get efficency
            eff = self._data_efficiency.loc[tech_name, "efficiency"]
            if 'heat' in tech_name and 'pump' in tech_name:
                carnot = (self.temp_building[:, 1] + self.zero_abs) / np.abs(self.temp_building[:, 1] - self._temp_ext)
                eff = eff * np.sum(carnot * self.temp_building[:, 0] / 100)

            # get final energy
            final_energy[tech_name] = data_heating[tech_name0]/eff

        return final_energy

    def get_energy_primary(self, data_heating):
        """
       The function computes the primary energy from different technology based on useful energy.
       :param data_heating: A dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
       :return: a Dataframe with the primary energy by technology by year by scenarios in kWh
       """

        # create the output dataframe
        primary_ener = _create_empty_output(data_heating)
        # compute renewable
        for tech_name in primary_ener .columns[2:]:
            primary_coeff = self._kbob.get_value(tech_name, 'EP_Global', language="ENG", ener_type='useful')
            primary_ener[tech_name] = primary_coeff * data_heating[tech_name]

        return primary_ener

    def get_capex(self,data_heating_power, interp=1):
        """
        The function return the CAPEX of the heating data based on the installed power in kW. CAPEX is capital cost.
        Careful the other function needs primary energy as input. This one needs power.
        :param data_heating_power: A dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
        :param interp: the interpolation method for the price database
        :return: a dataframe with operational cost.
        """

        # create the output dataframe
        capex = _create_empty_output(data_heating_power)

        # compute capex
        for tech_name in capex.columns[2:]:
            for ind in capex.index:
                capex.loc[ind, tech_name] = self._price.get_price(tech_name, 'CAPEX',
                                                                 unit_size=data_heating_power.loc[ind, tech_name],
                                                                 interp_choice=interp)

        return capex

    def get_opex(self, data_heating_power, interp=1):
        """
        The function return the OPEX of the heating data based on the installed power in kW. OPEX is operational cost.
        Careful the other functions need primary energy as input. This one needs power.

        The estimation of matenance is not precise. It contains the price tpo buy the fuel but it is not corrected for
        the real consumption. So it is just a rough estimation.

        :param data_heating_power: A dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
        :param interp: the interpolation method for the price database
        :return: a dataframe with operational cost.
        """

        # create the output dataframe
        opex = _create_empty_output(data_heating_power)

        # compute opex
        for tech_name in opex.columns[2:]:
            for ind in opex.index:
                opex.loc[ind, tech_name] = self._price.get_price(tech_name, 'OPEX',
                                                                 unit_size=data_heating_power.loc[ind, tech_name],
                                                                 interp_choice=interp)

        return opex

    def set_ext_temp(self, temp_ext):
        """
        To set the exterior temperature for the efficiency of the heat pumps
        :param temp_ext: the exteriot temperature in Celsius
        """
        self._temp_ext = temp_ext

    def get_reference(self, kpi, tech_name=''):
        """"
        get the reference for a kpi of interest.
        :param kpi: a string with the name of the kpi
        :param tech_name: the name of the technology of interest (necessary if the kpi is OPEX or CAPEX)
        :return a string if the underlining data is linked with kpi.py, a Series if the data is linked with price.py
        """

        if kpi.lower() in self.kpi_from_price:
            return self._price.get_reference_for_price(tech_name, kpi)
        else:
            return self._kbob.get_reference()



def _create_empty_output(data_heating):
    """
    This function create an empty dataframe with years and scenario which is used to return kpi data after the
    commutation
    :param data_heating: A dataframe with the following columns: scenario, year, <technology 1>, <technology 2>,...
    :return: a Dataframe with empty column and one column with the year and one column with the scenarios
    """

    # create the output dataframe
    empty_output = pd.DataFrame(0, index=data_heating.index, columns=data_heating.columns)
    empty_output['years'] = data_heating['years']
    empty_output['scenarios'] = data_heating['scenarios']

    return empty_output