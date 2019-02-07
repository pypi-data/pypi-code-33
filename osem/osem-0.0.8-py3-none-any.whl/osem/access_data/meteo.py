# this script loads and manage meteo data

import os
import pandas as pd
import numpy as np

from osem.general.helper import find_string
import osem.general.conf as conf

class Meteo:

    def __init__(self, year_id=None):

        # parameter for load data
        self._data_folder = conf.data_folder_meteo
        self._filenames = conf.filenames
        self._nbline_header = conf.nbline_header
        self._col_name = conf.col_name

        # data
        self._meteo_data, self._unit_data, self.reference = self._load_meteo_data()

        # other parameter
        self._cutoff = conf.cutoff

    def get_meteo_data_annual(self, met_param, station):
        """
        This function get annual value for a parameter
        :param met_param: the type of meterological parameters
        :param station: the name of the meteorological station (string)
        :return:
        """

        # get data
        met_param = find_string(met_param, self._meteo_data.keys(), self._cutoff)
        datam = self._meteo_data[met_param]
        station = find_string(station, datam['station_name'], self._cutoff)

        return datam.loc[datam['station_name'] == station, self._col_name[-1]].iloc[0]

    def get_meteo_data_monthly(self, met_param, station, months):
        """
       This function get monthly value for a parameter
       :param met_param: the type of meterological parameter
       :param station: the name of the meteorological station (string)
       :param months: the months of interest as string or as int (0 is january)
       :return: A list with the value of the month of interest
       """
        # get whole data
        met_param = find_string(met_param, self._meteo_data.keys(), self._cutoff)
        datam = self._meteo_data[met_param]
        station = find_string(station, datam['station_name'], self._cutoff)

        # get data by month
        months = list(months)
        data_month = []
        jan_ind = datam.columns.get_loc(conf.month_name[0])
        for m in months:
            if isinstance(m, float) or isinstance(m, int):
                data_month.append(float(datam.loc[datam['station_name'] == station,:].iloc[:, jan_ind + m]))
            else:
                m_name = find_string(m, conf.month_name, self._cutoff)
                data_month.append(datam.loc[datam['station_name'] == station, m_name].iloc[0])

        return data_month

    def get_unit(self, met_param):
        """
        This funtion return the units of the meteorological parameter
        :param met_param: the type of meterological parameter
        """
        met_param = find_string(met_param, self._meteo_data.keys(), self._cutoff)

        return self._unit_data[met_param].strip()


    def get_meteo_parameter(self):
        """

        :return: A list of string with the name of the parameters
        """
        return list(self._meteo_data.keys())

    def get_meteo_station(self, met_param, return_coord=False):
        """
        This function get the meteorological station available for a particular meteorological parameter
        :param met_param: the type of meteorological parameter of interest
        :param return_coord: If True, the coordinates (CH1903/LV95) are returned with the station
        :return: A Serie of string which are the station name (and maybe the coordinates)
        """
        met_param = find_string(met_param, self._meteo_data.keys(), self._cutoff)

        if return_coord:
            return self._meteo_data[met_param].loc[:, ['station_name', 'coordinates_CH']]
        else:
            return self._meteo_data[met_param].loc[:, 'station_name']

    def get_closest_station(self, met_param, coordinates, altitude=None, max_alt_diff=None):
        """
        This function finds the station which is the closest to a point described by its coordinates. If an altitude
        and a maximum altitude difference is given, it finds the closest station within the altitude difference.
        :param met_param: the type of meteorological parameter of interest
        :param coordinates: The coordinates of the study area in the coordinate system CH1903/LV95
        :param altitude: the altitude at the coordinate at the point of interest (optional)
        :param max_alt_diff: the max altitude difference between the station and the point of interest (opt)
        :return: the characteristics of the station (name, altitude, distance, coordinate) in a Series
        """

        # get data
        met_param = find_string(met_param, self._meteo_data.keys(), self._cutoff)
        datam = self._meteo_data[met_param]

        # add constraint on altitude
        if altitude is not None and max_alt_diff is not None:
            datam = datam.loc[abs(datam['elev_m'] - altitude) < max_alt_diff, 'elev_m']

        # get distance
        dist = np.sqrt((coordinates[0]-datam['coord_x'])**2 + (coordinates[1]-datam['coord_y'])**2).values
        arg_min_dist = np.argmin(dist)
        dist_min = dist[arg_min_dist]

        # return data
        sta = datam.iloc[arg_min_dist, :]
        sta = pd.concat((sta, pd.Series(data=[dist_min], index=['distance_m']))) # avoid warning
        return sta[['station_name', 'elev_m', 'coordinates_CH', 'distance_m']]

    def get_reference(self, met_param):
        """
        retrun the reference of the data for the meterological parameter of interest.
        :param met_param: the type of meteorological parameter of interest
        """

        met_param = find_string(met_param, self._meteo_data.keys(), self._cutoff)
        return self.reference[met_param]

    def _load_meteo_data(self):
        """
        This function loads the climatological data and put this data in Dataframe. One Dataframe by type of
        climatological variable. All the Dataframe in a dictionary.
        :return: A dictionary of Dataframe, one Dataframe by type of meteorological data
        """

        meteo_data = {}
        unit_data = {}
        ref_data = {}
        for f in self._filenames:

            # load data
            key = os.path.splitext(f)[0]
            filename_here = os.path.join(self._data_folder, f)
            datam = pd.read_csv(filename_here, header=self._nbline_header, sep='\t')
            datam.columns = self._col_name

            # correct the form of the coordinate
            datam['coord_x'], datam['coord_y'] = datam['coordinates_CH'].str.split('/', 1).str
            datam['coord_x'] = datam['coord_x'].apply(float)
            datam['coord_y'] = datam['coord_y'].apply(float)

            # obtain units
            with open(os.path.join(self._data_folder, f), encoding='utf-8') as f:
                content = f.readlines()
            unit_here = content[conf.line_with_unit].split('/')[1]

            # get the reference

            with open(filename_here, encoding='utf-8') as myfile:
                ref_here = [next(myfile) for x in range(self._nbline_header)]
            ref_here = " ".join(ref_here)

            # give it to the dict
            meteo_data[key] = datam
            unit_data[key] = unit_here
            ref_data[key] = ref_here


        return meteo_data, unit_data, ref_data


