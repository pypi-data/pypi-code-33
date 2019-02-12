#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Python codes to analyse airline data
"""


import os
import datetime
import numpy as np
import pandas as pd


class DirectOperationalCostsData:
    """
    Analyses airline direct operational costs based on a F41 Schedule P5.2 database from the United States Department
    of Transportation
    """

    # Minimum air hours filter (in thousands)
    filter_min_air_hours = 0.1
    # Nan filter
    filter_nan = True

    def __init__(self, database='databases\F41SCHEDULE_P52_18082017'):
        """Explanatory tables for *aircraft_type* and *aircraft_group* are available in the database."""

        self.database = database
        self.aircraft_type = None
        self.aircraft_group = None
        self.year = datetime.datetime.now().year - 1

    def filter(self, column, filter, raw_data):
        """Utility function to extract rows from dataframe where *column* must equal *filter*. Filter may be either
        a single value or an array."""

        filtered_data = []

        if isinstance(filter, (list, tuple, np.ndarray)):
            for f in filter:
                filtered_data.append(raw_data[getattr(raw_data, column) == f])
            return pd.concat(filtered_data)

        else:
            filtered_data = raw_data[getattr(raw_data, column) == filter]
            return filtered_data

    def get(self):
        """Utility function to extract relevant data based on settings"""

        data = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                        self.database,
                                        'T_F41SCHEDULE_P52_All_All.csv'))
        self.columns = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                self.database,
                                                'L_COSTS.csv_'))

        # Aircraft type
        if self.aircraft_type:
            data = self.filter('AIRCRAFT_TYPE', self.aircraft_type, data)
        # Aircraft group
        if self.aircraft_group:
            data = self.filter('AIRCRAFT_GROUP', self.aircraft_group, data)
        # Years
        data = self.filter('YEAR', self.year, data)
        # Other
        data = data[data.TOTAL_AIR_HOURS.astype('float') >= self.filter_min_air_hours]
        data = pd.DataFrame(data, columns=self.columns.name)
        if self.filter_nan:
            data = data.dropna()
        data = data.astype('float')
        # Save
        self.data = data
        self.samples = len(data.index)
        # Averaging
        self.average = data.div(data['TOTAL_AIR_HOURS'], axis='index')

    def analyse(self):
        """Analyse the data and split it up according to a FAA convention (GRA, Incorporated-Economic Counsel to the
         Transportation Industry, Economic Values for FAA Investment and Regulatory Decisions, FAA OAPP, 2015)"""

        self.get()

        fuel = self.average.FUEL_FLY_OPS + self.average.OIL_FLY_OPS + self.average.OTH_TAX_FLY_OPS
        maintenance = self.average.AIRFRAME_LABOR + self.average.ENGINE_LABOR + self.average.AIRFRAME_REPAIR + \
                      self.average.ENGINE_REPAIRS + self.average.INTERCHG_CHARG + self.average.AIRFRAME_MATERIALS + \
                      self.average.ENGINE_MATERIALS + self.average.AIRFRAME_ALLOW + self.average.AIRFRAME_OVERHAULS + \
                      self.average.ENGINE_ALLOW + self.average.ENGINE_OVERHAULS + self.average.AP_MT_BURDEN + \
                      self.average.NET_OBSOL_PARTS
        crew = self.average.PILOT_FLY_OPS + self.average.OTH_FLT_FLY_OPS + self.average.TRAIN_FLY_OPS + \
               self.average.PERS_EXP_FLY_OPS + self.average.BENEFITS_FLY_OPS + self.average.PAY_TAX_FLY_OPS
        depreciation = self.average.AIRFRAME_DEP + self.average.ENGINE_DEP + self.average.PARTS_DEP + \
                       self.average.ENG_PARTS_DEP + self.average.OTH_FLT_EQUIP_DEP
        rentals = self.average.INTERCHG_FLY_OPS + self.average.RENTAL_FLY_OPS + self.average.FLT_EQUIP_A_EXP
        insurance = self.average.INS_FLY_OPS
        others = self.average.INCIDENT_FLY_OPS + self.average.OTHER_EXP_FLY_OPS + self.average.OTHER_FLY_OPS + \
                 self.average.PRO_FLY_OPS

        result = np.array([(fuel.mean(), 'Fuel'),
                           (maintenance.mean(), "Maintenance"),
                           (crew.mean(), 'Crew'),
                           (depreciation.mean(), 'Depreciation'),
                           (rentals.mean(), 'Rentals'),
                           (insurance.mean(), 'Insurance'),
                           (others.mean(), 'Others')],
                           dtype=[('val', 'f4'), ('key', 'S10')])

        return result
