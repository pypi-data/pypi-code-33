"""
Utilities for loading historical weather data from NOAA's GSOD datasets.
Metadata: ftp://ftp.ncdc.noaa.gov/pub/data/gsod/GSOD_DESC.txt

This data is definitely public and requires no logging in or tokens.

There exist python packages like WunderWeather, openweather, weather-api
(with forecasts), openweathermap which may provide more timely data.
get-weather-data looks public, but complicated to use (needs NCDC tokens).
"""


## imports
import urllib
import sys, os, inspect
import tempfile
import pandas
import datetime
import warnings

from ftk.time_series_data_frame import TimeSeriesDataFrame

try:
    from azuremltkbase.exceptions.exception import DataFrameValueException
except ImportError:
    from ftk.exception import DataFrameValueException


def load_station_database():
    """
    Read the list of NOAA stations from local csv file.

    :return: A dataframe of weather stations.
    """

    this_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    database_file = os.path.join(this_dir, 'isd-history.csv');
    df = pandas.read_csv(database_file)
    return df
    

def _parse_num_with_flag(num_with_flag:str):
    """ 
    Parse a number, followed optionally by a single-character, non-digit flag,
    into its constituent parts
    """

    num = float('nan')
    flag = ""
    if str.isdigit(num_with_flag[-1]):
        # there is no flag
        num = float(num_with_flag)
    else:
        flag = num_with_flag[-1]
        num = float(num_with_flag[:-1])

    return num, flag



def get_a_year_of_daily_weather_data(stn=725300, wban=94846, year=1990):
    """
    Get weather data for a particular weather station.
    Consider using get_all_daily_weather_data_for_station() for a cleaner interface.

    Use ftk.data.weather.load_noaa_weather_data._load_station_database()
    to find the STN and WBAN numbers for the weather station you need.

    Will cache data locally in the temp directory to speed up repeated pulls.

    :param stn:
        Weather station's STN number. Default values corresponds to Chicago O'Hare.
        Either none or both of STN and WBAN arguments need to be provided.
    :type stn:
        int
    :param wban:
        Weather station's WBAN number. Default value corresponds to KORD.
        Either none or both of STN and WBAN arguments need to be provided.
    :type wban:
        int
    :param year:
        The year for which data is needed. 
    :type year:
        int
    :return:
        TimeSeriesDataFrame object containing daily weather summary
        of a user provided weather station for a given year.
    """

    # where stuff is
    temp_directory=tempfile.gettempdir()
    file_name = '{}-{}-{}.op.gz'.format(stn, wban, year);
    url = 'ftp://ftp.ncdc.noaa.gov/pub/data/gsod/{}/{}'.format(year, file_name);
    local_copy = os.path.join(temp_directory, file_name);

    # get a local copy if we don't have yet
    if not os.path.isfile(local_copy):
        try:            
            urllib.request.urlretrieve(url, local_copy)
        except urllib.error.URLError:
            pass
            # No worries, station probably didn't exist in that year.
            # We'll warn the user in the next step.

    # if we did find that data
    if os.path.isfile(local_copy):
        # compressions only supported in newer pandas versions        
        data_frame = pandas.read_csv(local_copy, compression='infer', 
                                     delim_whitespace=True, 
                                     header=None, skiprows=1, # skip header row (incomplete)
                                     names = [
                                        'STN', 'WBAN', 'YEARMODA', 
                                        'TEMP', 'TEMPCount', 'DEWP', 'DEWPCount', 
                                        'SLP', 'SLPCount', 'STP', 'STPCount',
                                        'VISIB','VISIBCount','WDSP','WDSPCount',
                                        'MXSPD', 'GUST', 'MAX', 'MIN',
                                        'PRCP', 'SNDP', 'FRSHTT'
                                         ],
                                     parse_dates = ['YEARMODA']
                                     )        
        
        data_frame.set_index(['STN', 'WBAN', 'YEARMODA'], inplace=True)
        
        # drop any duplicates that may exist
        processed = data_frame[~data_frame.index.duplicated(keep='first')];

        # post-process everything here - get the flags out of the columns that have it 
        # and are therefore recognized as "string" (MAX, MIN, PRCP).
        processed = processed.assign(MAXFlag = processed.loc[:, 'MAX'].apply(lambda s: _parse_num_with_flag(s)[1])) \
                             .assign(MAX = processed.loc[:, 'MAX'].apply(lambda s: _parse_num_with_flag(s)[0]))     \
                             .assign(MINFlag = processed.loc[:, 'MIN'].apply(lambda s: _parse_num_with_flag(s)[1])) \
                             .assign(MIN = processed.loc[:, 'MIN'].apply(lambda s: _parse_num_with_flag(s)[0]))      \
                             .assign(PRCPFlag = processed.loc[:, 'PRCP'].apply(lambda s: _parse_num_with_flag(s)[1])) \
                             .assign(PRCP = processed.loc[:, 'PRCP'].apply(lambda s: _parse_num_with_flag(s)[0]))     \

        # process special value 999 for GUSTs, STP and SNDP (snow depth)
        processed = processed.assign(GUST = processed.loc[:, 'GUST'].apply(lambda v: float(v) if v < 999.0 else float('nan'))) \
                             .assign(STP = processed.loc[:, 'STP'].apply(lambda v: float(v) if v < 999.0 else float('nan'))) \
                             .assign(SNDP = processed.loc[:, 'SNDP'].apply(lambda v: float(v) if v < 999.0 else float('nan')))

        return TimeSeriesDataFrame(processed, 
                                   time_colname='YEARMODA', 
                                   grain_colnames=['STN'], 
                                   ts_value_colname='TEMP');
    else:
        # We could not get the data
        wstring = 'Data was not found for {}-{}-{}'.format(stn, wban, year)
        warnings.warn(wstring);
        return None


def get_all_daily_weather_data_for_station(stn:int=725300, start_year:int=2000, end_year:int=None):
    """
    Gets all data for a user specified station starting with the year `start_year`
    and ending with `end_year`. end_year defaults to today and is not retrieved
    because this year is incomplete.

    Use `ftk.data.weather.load_noaa_weather_data.load_station_database`()
    to find the STN number for the weather station you need.

    :param stn: 
        Weather station number. It corresponds to 'USAF' column in the database. 
    :type stn:
        int
    :param start_year: 
        Get weather data starting with this year.
    :type start_year:
        int
    :param end_year: 
        Get weather data ending with this year (not inclusive).
    :type start_year:
        int
    :return:
        TimeSeriesDataFrame object containing daily weather summary
        of a user provided weather station.
    """
    dbdf = load_station_database();
    station = dbdf[dbdf['USAF']==stn]

    if len(station) == 0:
        raise DataFrameValueException('The station STN={} was not found in DB.'.format(stn))
    if len(station) > 1:
        warnings.warn('Found more than one station with STN id {}. Will use the first.'.format(stn))

    wban = station.iloc[0]["WBAN"];

    if end_year is None:
        end_year = datetime.datetime.today().year

    print('This retrieval from NOAA may take a bit')    
    years = [ get_a_year_of_daily_weather_data(stn, wban, year)
              for year in range(start_year, end_year)]
    
    alldata = pandas.concat([d for d in years if d is not None])    
    return alldata

###############################################################################
## Main

if __name__ == '__main__':
    
    # test loading of the station DB
    sdf = load_station_database()
    print(sdf.columns)
    
    # Find Portland by airport code
    portland = sdf[sdf['ICAO']=='KPDX']
    portland_stn = portland.iloc[0]["USAF"]
    print(portland)             
 
    # test pulling the data
    wdf = get_a_year_of_daily_weather_data()
    print(wdf[1:10])

    # Seattle is STN=727930
    adf = get_all_daily_weather_data_for_station(start_year=2000, stn=727930, end_year=2003)
    print(adf[1:10])

    adf = get_all_daily_weather_data_for_station(start_year=2000, stn=portland_stn)
    print(adf[1:10])









