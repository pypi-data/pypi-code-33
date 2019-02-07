import os
import pandas as pd
import numpy as np
import sqlite3
from scipy import interpolate
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from collections import OrderedDict
import warnings

from osem.general.helper import find_string, func_logarithm, rsquared
import osem.general.conf as conf


class Price:
    """
    This class loads and interpolate the price data
    """

    def __init__(self):

        # parameter
        self._data_folder = conf.data_folder
        self._cutoff = conf.cutoff
        self._precision = conf.precision_price
        self._basename_price = conf.basename_price
        self._column_not_print = conf.column_not_print_price
        self._name_tableunit = conf.name_tableunit
        self._myind = conf.myind
        self._ref_col = conf.ref_col  # name of the column with the references
        self._nb_point_graph = conf.nb_point_graph
        self._interp_lim = conf.interp_lim

        # data
        self.db_price, self._units = self._load_price_data()
        self._techno_list = list(self.db_price.keys())

        # silence warning
        warnings.filterwarnings('ignore', conf.warning_ignore)

    def get_technology_available(self):
        """
        This function return the list of technology available
        """
        return self._techno_list

    def get_type_of_price_available(self, techno_choice):
        """
        This function return the type of price (installation, CAPEX, maintenance, etc.) available for the technology
        :param techno_choice: string - the name of the technology of interest
        """
        techno_correct = find_string(techno_choice, self._techno_list, self._cutoff)
        price_type = [c for c in self.db_price[techno_correct].columns if c not in self._column_not_print]

        return price_type

    def get_reference_for_price(self, techno_choice, price_choice):
        """
        This function return the references used to compute the price
        :param techno_choice: string - the name of the technology of interest
        :param price_choice: string - the type of price (CAPEX, OPEX, etc)
        :return: a Series with the unit size as key and reference as values
        """
        # find correct string
        techno_correct, price_correct = self._get_techno_and_price(techno_choice, price_choice)

        # get reference for price which exists (not null)
        db_techno = self.db_price[techno_correct]
        reference = db_techno.loc[~db_techno[price_correct].isnull(), self._ref_col]
        return reference

    def get_units(self, techno_choice):
        """
        This function returns the type of units for each technology. In other words, is the price given by m2, by kW or
        by m, etc.
        :param techno_choice: string - the name of the technology of interest
        :return: a string representing the unit
        """
        techno_correct = find_string(techno_choice, self._techno_list, self._cutoff)

        return self._units[techno_correct]

    def get_price(self, techno_choice, price_choice, unit_size=1, interp_choice=1, param_lim_inter=None, bounds=None):
        """
        This function compute the price of the different technology.

        :param techno_choice: string - the name of the technology of interest
        :param price_choice: string - the type of price (CAPEX, OPEX, etc)
        :param unit_size: float - the size of unit (only one unit)
        :param interp_choice: string/int/function - the type of interpolation, can be polynomial (int) or the strings
               [log, spline] or a function
        :param param_lim_inter: list of float, optional - the computed parameters for the interpolations, used if the
               same computation is done many times.
        :param bounds: 2-tuple of array_like, optional - lower and upper bounds on parameters.
        :return: the price as float
        """

        # get interpolation parameter
        if not param_lim_inter:
            param_inter, lim_param = self._get_interpolation_param(techno_choice, price_choice, interp_choice,
                                                                  bounds=bounds)
        else:
            param_inter = param_lim_inter[0]
            lim_param = param_lim_inter[1]

        # check size
        if unit_size < lim_param[0]*(1-self._interp_lim) or unit_size > lim_param[1]*(1+self._interp_lim):
            raise Warning("The size given is out of the interpolation range ({},{})".format(lim_param[0], lim_param[1]))

        # get price
        if isinstance(interp_choice, int):
            price = np.polyval(param_inter, unit_size)
        elif interp_choice == 'spline':
            price = interpolate.splev(unit_size, param_inter)
        elif interp_choice == 'logarithm':
            price = func_logarithm(unit_size, *param_inter[0])
        elif callable(interp_choice):  # if function
            price = interp_choice(unit_size, *param_inter[0])
        else:
            raise ValueError("The interpolation choice {} is not known.".format(str(interp_choice)))

        return np.float(price)

    def get_price_for_many_units(self, techno_choice, price_choice, unit_size, interp_choice=1, bounds=None):
        """
        This function compute the price of the different technology for a list of units size.

        :param techno_choice: string - the name of the technology of interest
        :param price_choice: string - the type of price (CAPEX, OPEX, etc)
        :param unit_size: list of float - the size of units
        :param interp_choice: string/int/function - the type of interpolation, can be polynomial (int) or the strings
               [log, spline] or a function
        :param bounds: 2-tuple of array_like, optional - lower and upper bounds on parameters.
        :return: list of float with the price
        """

        # get interpolation parameter
        param_inter, lim_param = self._get_interpolation_param(techno_choice, price_choice, interp_choice, bounds=bounds)

        # compute price for each size without re-computing the interpolation parameters
        all_price = []
        for s in unit_size:
            price_here = self.get_price(techno_choice, price_choice, s, interp_choice, [param_inter, lim_param])
            all_price.append(price_here)

        return all_price

    def _get_interpolation_param(self, techno_choice, price_choice, interp_choice=1, bounds=None):
        """
        This function returns the parameter for the interpolation. The interpolation choice can be an int if polynomial,
        a function (least-square fitting) or the string "spline" or "logarithm"

        :param techno_choice: string - the name of the technology of interest
        :param price_choice: string - the type of price (CAPEX, OPEX, etc)
        :param interp_choice: string/int/function - the type of interpolation, can be polynomial (int) or the strings
               [logarithm, spline] or a function
        :param bounds: 2-tuple of array_like, optional - lower and upper bounds on parameters.
        :return: a list with the interpolation parameters, a list with the range of the interpolation
        """
        # find correct string
        techno_correct, price_correct = self._get_techno_and_price(techno_choice, price_choice)
        db_techno = self.db_price[techno_correct]

        # get data without nan
        price_here = db_techno[price_correct].dropna()
        unit_here = price_here.index

        # get parameters for the different interpolation
        if isinstance(interp_choice, int):    # polynomial
            param_inter = np.polyfit(unit_here, price_here, interp_choice)
        elif interp_choice == 'spline':  # smooth interpolation
            if len(price_here) <= 3:
                order_spline = len(price_here)-1
            else:
                order_spline = 3
            if len(list(set(unit_here))) != len(unit_here):
                raise ValueError("Spline interpolation needs unique values.")
            param_inter = interpolate.splrep(unit_here, price_here, k=order_spline)
        elif interp_choice == 'logarithm':  # logarithmic
            param_inter = curve_fit(func_logarithm, unit_here, price_here, bounds=([-np.inf, 0, -np.inf], np.inf))
        elif callable(interp_choice):  # custom function
            if bounds:
                param_inter = curve_fit(interp_choice, unit_here, price_here, bounds=bounds)
            else:
                param_inter = curve_fit(interp_choice, unit_here, price_here)
        else:
            raise ValueError("The interpolation choice {} is not known.".format(str(interp_choice)))

        # interpolation range
        lim_param = [min(unit_here), max(unit_here)]

        return param_inter, lim_param

    def create_fig_price(self, techno_choice, price_choice, show=True):
        """
        This function creates a figure which shows the unit (x-axis) and price (y-axis) to help to prepare the user
        for the interpolation.
        :param techno_choice: string - the name of the technology of interest
        :param price_choice: string - the type of price (CAPEX, OPEX, etc)
        :param show: Bool - If True, show the figure one screen and pause the execution
        :return: the matplotlib figure
        """
        # find correct string
        techno_correct, price_correct = self._get_techno_and_price(techno_choice, price_choice)

        # create figure
        db_techno = self.db_price[techno_correct]
        figprice = plt.figure()
        plt.plot(db_techno.index, db_techno[price_correct], "*")
        plt.title('Price for ' + techno_choice)
        plt.xlabel('Units [{}]'.format(self._units[techno_correct]))
        plt.ylabel(price_correct + ' [CHF]')
        if show:
            plt.show()

        return figprice

    def create_fig_interpolation(self, techno_choice, price_choice, interp_choice, show=True, bounds=None):
        """
        This function creates a figure which shows the unit (x-axis) and price (y-axis) with the interpolation
        to judge the quality of the interpolation
        :param techno_choice: string - the name of the technology of interest
        :param price_choice: string - the type of price (CAPEX, OPEX, etc)
        :param interp_choice: string/int/function - the type of interpolation, can be polynomial (int) or the strings
               [logarithm, spline] or a function
        :param bounds: 2-tuple of array_like, optional - lower and upper bounds on parameters.
        :param show: bool - If True, show the figure one screen and pause the execution
        :return: the matplotlib figure
        """

        # get interpolation parameter
        param_inter, lim_param = self._get_interpolation_param(techno_choice, price_choice, interp_choice)

        # get interpolated price
        size_units = np.linspace(lim_param[0], lim_param[1], self._nb_point_graph)
        prices_inter = self.get_price_for_many_units(techno_choice, price_choice, size_units, bounds=bounds)

        # get correlation parameter
        techno_correct, price_correct = self._get_techno_and_price(techno_choice, price_choice)
        db_techno = self.db_price[techno_correct]
        prices_ini = db_techno[price_correct].dropna()
        prices_inter_r2 = self.get_price_for_many_units(techno_choice, price_choice, prices_ini.index, bounds=bounds)
        r2 = rsquared(prices_ini, prices_inter_r2)

        # plot the price
        figprice = self.create_fig_price(techno_choice, price_choice, False)
        plt.plot(size_units, prices_inter)
        plt.text(max(size_units)/20, max(prices_inter), "R^2: "+str(r2))
        if show:
            plt.show()

        return figprice

    def _get_techno_and_price(self, techno_choice, price_choice):
        """
        This function takes the string from the user with his/her choice of technology and price and return them in the
        correct form
        :param techno_choice: string - the name of the technology of interest
        :param price_choice: string - the type of price (CAPEX, OPEX, etc)
        :return:
        """

        techno_correct = find_string(techno_choice, self._techno_list, self._cutoff)
        if price_choice == 'OPEX':
            price_choice = conf.opex_name

        price_type = [c for c in self.db_price[techno_correct].columns if c not in self._column_not_print]
        price_correct = find_string(price_choice, price_type, self._cutoff)

        return techno_correct, price_correct

    def _load_price_data(self):
        """
        This function loads the sqlite database  which contain the data about the price.
        :return: A ordered dict of DataFrame with the price data. One dataframe by technology.
                 + A dict with the technology as keys and the units as values.
        """

        db_price = OrderedDict()
        units = {}

        # open database
        db_base = sqlite3.connect(os.path.join(self._data_folder, self._basename_price))
        cursor = db_base.cursor()
        # read table name
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table_name in tables:
            # read the whole table data and column name
            table_name = table_name[0]
            cursor.execute("SELECT * from {}".format(table_name))
            table = cursor.fetchall()
            col_name = list(map(lambda x: x[0], cursor.description))
            # manage null before we create a pandas dataframe with mixed colmun types
            table = [tuple((np.nan if item=='NULL' else item) for item in t) for t in table]
            table = pd.DataFrame(data=table, columns=col_name)
            if table_name != self._name_tableunit:
                table = table.drop([self._myind], axis=1)
                table.set_index(table.columns[0], inplace=True)
                db_price[table_name] = table
            else:
                units = pd.Series(table.iloc[:, 1].values,index=table.iloc[:, 0]).to_dict()

        return db_price, units
