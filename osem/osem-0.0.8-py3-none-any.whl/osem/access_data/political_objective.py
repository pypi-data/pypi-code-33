import os
import pandas as pd
from osem.general.helper import find_string
import osem.general.conf as conf


class PoliticalObjective:
    """
    This class loads the political objectives
    """

    def __init__(self):

        # parameter
        self._data_folder = conf.data_folder
        self._cutoff = conf.cutoff
        self._basename_pol = conf.basename_pol
        self._column_not_print = conf.column_not_print_pol

        # load data
        self.db_obj = pd.read_csv(os.path.join(self._data_folder, self._basename_pol), sep=";")
        self.db_obj.set_index("political_framework", inplace=True)
        self._name_objective = [c for c in self.db_obj.columns if c not in self._column_not_print]

    def get_objective(self, politic_type, objective_type, return_year=True):

        """
        This function return the political objective
        :param objective_type: string - the type of objective (C02 emisson, primary energy, etc.)
        :param politic_type: string - the name of the political frame work
        :param return_year: bool- if True return the reference and objective year
        """

        # match the strings proposed by the user
        objective_found = find_string(objective_type, self._name_objective, self._cutoff)
        politic_found = find_string(politic_type, self.db_obj.index, self._cutoff)

        # get the objective
        objective_value = self.db_obj.loc[politic_found, objective_found]

        # year
        if return_year:
            year_ref = self.db_obj.loc[politic_found, "reference_year"]
            year_obj = self.db_obj.loc[politic_found, "objective_year"]
            objective_dict = {'value': objective_value, 'year_ref':year_ref, 'year_obj': year_obj}
            return objective_dict
        else:
            return objective_value

    def get_politic_framework(self):
        """
        This function get the available political framework
        """
        return list(self.db_obj.index.values)

    def get_all_objectives(self):
        """
        This function get the type of objective available
        """
        return list(self._name_objective)

    def get_reference(self,politic_type):
        """Obtain a reference for the political objective of interest.
        :param politic_type: string - the name of the political frame work
        """

        politic_found = find_string(politic_type, self.db_obj.index, self._cutoff)
        return self.db_obj.loc[politic_found, "reference"].iloc[0]
