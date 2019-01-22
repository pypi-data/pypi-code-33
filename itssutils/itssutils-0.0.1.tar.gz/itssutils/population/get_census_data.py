# Shamelessly 'inspired' by https://github.com/OpenDataPolicingNC/Traffic-Stops/blob/master/tsdata/acs.py

import pandas as pd
import census  # pip install census
from us import states
from ..utils.secrets import CENSUS_API_KEY
import json

class CensusGetter(object):
    """ Get population data from the US Census """
    def __init__(self, year=2016):
        with open('itssutils/population/acs5_race_variables.json') as f:
            self.RACE_VARIABLES = json.load(f)
        self.VARIABLES =  ['NAME', 'GEO_ID'] + list(self.RACE_VARIABLES.keys())
        self.fips = states.IL.fips  # FIPS code for the state of IL
        self.year = year
        self.census_api = census.Census(CENSUS_API_KEY, year=year)

    def get_state(self):
        """ Get the data for the state of Illinois """
        return self.census_api.acs5.state(self.VARIABLES, self.fips)

    def get_all_counties(self):
        """ Gets all data for all IL counties """
        return self.census_api.acs5.state_county(self.VARIABLES, self.fips, census.ALL)

    def get_all_places(self):
        """ Gets all data for all IL places (e.g., cities/villages) """
        return self.census_api.acs5.state_place(self.VARIABLES, self.fips, census.ALL)

    def parse_response(self, response, state=False):
        """ Turn the API response into a pandas DataFrame """
        df = pd.DataFrame(response)
        df = df.rename(columns=self.RACE_VARIABLES)
        if state:
            df.loc[0, 'NAME'] = 'Illinois State'
        return df

    def create_full_df(self):
        """ Combine all the dataframes from state, county, and place together """
        print('Getting county-level data.')
        self.counties = self.get_all_counties()
        print('Getting place-level data.')
        self.places = self.get_all_places()
        print('Getting state-level data')
        self.state = self.get_state()
        state_df = self.parse_response(self.state, state=True)
        county_df = self.parse_response(self.counties)
        place_df = self.parse_response(self.places)
        self.data = pd.concat([state_df, county_df, place_df], axis=0, sort=True)
        self.data['clean_census_name'] = self.clean_names()
        self.data.name = str(self.year)
        return self.data

    def clean_names(self):
        """ Clean the place names for merging with the agency names"""
        def _clean_name(place_name):
            place = place_name.split(',')[0]
            if len(place.split()) == 1:
                return place.lower()
            bad_words = ['village', 'town', 'city', 'CDP']
            for word in bad_words:
                place = place.replace(word, '')
            return ''.join(place.split()).lower()

        clean_census_names = self.data.NAME.apply(_clean_name)
        return clean_census_names

    def to_csv(self, out_path):
        """ Write a census data csv to out_path """
        self.create_full_df.to_csv(out_path, index=None)
