import os
import pandas as pd

from osem.general.helper import find_string
import osem.general.conf as conf


class Kbob:
    """
    This class loads and manipulate the kbob data
    """

    LANG = ["ENG", "FRA", "GER"]

    def __init__(self, year_id=None):

        # default parameter
        self._data_folder = conf.data_folder_kbob
        self._version_default = conf.version_default
        self._basename_unit = conf.basename_unit
        self._basename_kbob = conf.basename_kbob
        self._filename_trans_ind = conf.filename_trans_ind
        self._cutoff = conf.cutoff

        #  kbob creation
        if year_id:
            self.version = year_id
        else:
            self.version = self._version_default
        self.data, self.unit, self.index_translation = self._load_kbob()
        self.ref_kbob = conf.ref_kbob

    def get_value(self, techno, indicator, language="ENG", ener_type=None):
        """
        This function load one value of the kbob as a function of the user choice

        :param techno: string - the technology chosen
        :param indicator: string - the requested indicator
        :param language: string - the requested language
        :return: float - the value of the indicator
        """
        self._check_language(language)

        # in case we only want useful or final energy
        if ener_type is not None:
            all_techno = self.data.loc[self.data["EnerType"] == ener_type, :]
            all_techno = all_techno[language].values.tolist()
        else:
            all_techno = self.data[language].values.tolist()

        # find string
        tech_found = find_string(techno, all_techno, self._cutoff)
        indi_found_lang = find_string(indicator, self.index_translation[language], self._cutoff)

        indi_found = self.index_translation.loc[self.index_translation[language] == indi_found_lang, 'ENG'].values[0]

        return self.data.loc[self.data[language] == tech_found, indi_found].values[0]

    def get_units(self, choice_col):
        """
        This function return the units of the different data type
        :return: the unit as string
        """
        name_found = find_string(choice_col, self.data.columns, self._cutoff)
        if not name_found:
            raise ValueError("The requested data {} does not match any entry.".format(choice_col))

        return self.unit[name_found].values[0]

    def get_available_technologies(self, language="ENG", ener_type=None):
        """
        The function return the available technology
        :param language: string - the requested language
        :return a list of available technology
        """
        self._check_language(language)

        if ener_type is not None:
            all_techno = self.data.loc[self.data["EnerType"] == ener_type, :]
            return list(all_techno[language].values)
        else:
            return list(self.data[language].values)


    def get_available_indicators(self, language="ENG"):
        """
        Give access to the names of the available indicators in different language
        :return: a list of available indicators
        """
        self._check_language(language)
        return list(self.index_translation[language])

    def get_kbob_version(self):
        """
        Return the version (year) of the kbob used
        """

        return self.version

    def change_to_default_version(self):
        """
        Restore the loaded kbob to the default version
        """
        self.version = self._version_default
        self.data, self.unit, self.index_translation = self._load_kbob()

    def change_version(self, version_new):
        """
        Change the loaded kbob to the version chosen
        """
        self.version = str(version_new)
        self.data, self.unit, self.index_translation = self._load_kbob()

    def get_filenames(self):
        """
        Return the namre of the files used to load the kbob (dict of string)
        """
        filename_kbob = os.path.join(self._data_folder, self._basename_kbob + self.version + '.csv')
        filename_unit = os.path.join(self._data_folder, self._basename_unit + self.version + '.json')
        filename_trans = os.path.join(self._data_folder, self._filename_trans_ind)

        return {'kbob': filename_kbob, 'unit': filename_unit, 'translation': filename_trans}

    def get_reference(self):
        """
        return the reference paper for the kbob database
        """
        return self.ref_kbob

    def _load_kbob(self):
        """
        This function loads the kbob data and the units related to it
        """

        filenames_kbob = self.get_filenames()

        kbob = pd.read_csv(filenames_kbob['kbob'], index_col=0)
        unit = pd.read_json(filenames_kbob['unit'], lines=True)
        index_translation = pd.read_csv(filenames_kbob['translation'], header=0)

        return kbob, unit, index_translation

    def _check_language(self, language):
        if language not in self.LANG:
            raise ValueError("The requested language {} is not supported.".format(language))
