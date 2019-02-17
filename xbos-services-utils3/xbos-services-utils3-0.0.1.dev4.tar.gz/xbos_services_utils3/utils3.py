import datetime
import pytz
import pandas as pd
import numpy as np
import yaml

from pathlib import Path

import os
XBOS_SERVICES_UTILS3_DATA_PATH = Path(os.environ["XBOS_SERVICES_UTILS3_DATA_PATH"])

'''
Utility constants
'''
NO_ACTION = 0
HEATING_ACTION = 1
COOLING_ACTION = 2
FAN = 3
TWO_STAGE_HEATING_ACTION = 4
TWO_STAGE_COOLING_ACTION = 5


def get_zones(bldg):
    """Gets the zones of the given building.
    :param bldg: (str) as given in /Buildings/building_names.yml
    :return list of zone names (str). """
    path = XBOS_SERVICES_UTILS3_DATA_PATH / "all_zones.yml"
    with open(path, "r") as f:
        data = yaml.load(f)
    if bldg not in data:
        raise KeyError("Building name is incorrect or does not exist.")
    return data[bldg]


def get_buildings():
    """Get all building names."""
    path = XBOS_SERVICES_UTILS3_DATA_PATH / "all_buildings.yml"
    with open(path, "r") as f:
        data = yaml.load(f)
    return data


def get_mdal_string_to_datetime(date_string, with_utc=True):
    """Gets datetime from string with format Year-Month-Day Hour:Minute:Second UTC. Note, string should be for utc
    time.
    :param date_string: string of format Year-Month-Day Hour:Minute:Second UTC.
    :param with_utc: boolean indicating wether to localize to UTC time.
    :returns datetime.time() object in UTC time or naive time. """
    date_datetime = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %Z")
    if with_utc:
        return date_datetime.replace(tzinfo=pytz.timezone("UTC"))
    else:
        return date_datetime


def get_mdal_datetime_to_string(date_object):
    """Gets string from datetime object.
    :param date_object. Timezone Aware
    :returns '%Y-%m-%d %H:%M:%S UTC' """
    date_object = date_object.astimezone(pytz.utc)
    return date_object.strftime('%Y-%m-%d %H:%M:%S') + ' UTC'


def get_window_in_sec(s):
    """Returns number of seconds in a given duration or zero if it fails.
       Supported durations are seconds (s), minutes (m), hours (h), and days(d)."""
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    try:
        return int(float(s[:-1])) * seconds_per_unit[s[-1]]
    except:
        return 0


def combine_date_time(time, date):
    """Combines the time and date to a combined datetime. Specific use in DataManager functions.
    :param time: (str) HH:MM
    :param date: (datetime)
    :returns datetime with date from date and time from time. With seconds as 0."""
    datetime_time = get_time_datetime(time)
    return date.replace(hour=datetime_time.hour, minute=datetime_time.minute, second=0, microsecond=0)


def get_time_datetime(time_string):
    """Gets datetime from string with format HH:MM.
    :param date_string: string of format HH:MM
    :returns datetime.time() object with no associated timzone. """
    return datetime.datetime.strptime(time_string, "%H:%M").time()


def decrement_to_start_of_day(date, interval):
    """Decrements the time of date by interval. Stops when decrementing further by interval causes date to go to the
    previous day.
    i.e. (new_time - date) % interval == 0 and (new_time - interval).day != date.day
    :param date: (datetime) date to use for rounding
    :param interval int:seconds.
    :return datetime new_time"""

    dt = datetime.timedelta(seconds=interval)
    curr_day = date.day
    while (date - dt).day == curr_day:
        date -= dt
    return date

def smart_resample(data, start, end, window, method):
    """
    Groups data into intervals according to the method used.
    Returns data indexed with start to end in frequency of interval minutes.
    :param data: pd.series/pd.df has to have time series index which can contain a span from start to end. Timezone aware.
    :param start: the start of the data we want. Timezone aware
    :param end: the end of the data we want (not inclusive). Timezone aware
    :param window: (int seconds) interval length in which to split data.
    :param method: (optional string) How to fill nan values. Usually use pad (forward fill for setpoints) and
                            use "interpolate" for approximate linear processes (like outside temperature. For inside
                            temperature we would need an accurate thermal model.)
    :return: data with index of pd.date_range(start, end, interval). Returned in timezone of start.
    NOTE: - If (end - start) not a multiple of interval, then we choose end = start + (end - start)//inteval * interval.
                But the new end will not be inclusive.
          - If end is beyond the end of the data, it will assume that the last value has been constant until the
              given end.
    """
    try:
        end = end.astimezone(start.tzinfo)
        data = data.tz_convert(start.tzinfo)
    except:
        raise Exception("Start, End, Data need to be timezone aware.")


    # make sure that the start and end dates are valid.
    data = data.sort_index()
    if not start <= end:
        raise Exception("Start is after End date.")
    if not start >= data.index[0]:
        raise Exception("Resample start date is further back than data start date -- can not resample.")
    if not window > 0:
        raise Exception("Interval has to be larger than 0.")

    # add date_range and fill nan's through the given method.
    date_range = pd.date_range(start, end, freq=str(window) + "S")
    end = date_range[-1]  # gets the right end.

    # Raise warning if we don't have enough data.
    if end - datetime.timedelta(seconds=window) > data.index[-1]:
        print("Warning: the given end is more than one interval after the last datapoint in the given data. %s minutes after end of data."
              % str((end - data.index[-1]).total_seconds()/60.))

    new_index = date_range.union(data.index).tz_convert(date_range.tzinfo)
    data_with_index = data.reindex(new_index)

    if method == "interpolate":
        data = data_with_index.interpolate("time")
    elif method in ["pad", "ffill"]:
        data = data_with_index.fillna(method=method)
    else:
        raise Exception("Incorrect method for filling nan values given.")

    data = data.loc[start: end]  # While we return data not inclusive, we need last datapoint for weighted average.

    def weighted_average_constant(datapoint, window):
        """Takes time weighted average of data frame. Each datapoint is weighted from its start time to the next
        datapoints start time.
        :param datapoint: pd.df/pd.series. index includes the start of the interval and all data is between start and start + interval.
        :param window: int seconds.
        :returns the value in the dataframe weighted by the time duration."""
        datapoint = datapoint.sort_index()
        temp_index = np.array(list(datapoint.index) + [datapoint.index[0] + datetime.timedelta(seconds=window)])
        diffs = temp_index[1:] - temp_index[:-1]
        weights = np.array([d.total_seconds() for d in diffs]) / float(window)
        assert 0.99 < sum(weights) < 1.01  # account for tiny precision errors.
        if isinstance(datapoint, pd.DataFrame):
            return pd.DataFrame(index=[datapoint.index[0]], columns=datapoint.columns, data=[datapoint.values.T.dot(weights)])
        else:
            return pd.Series(index=[datapoint.index[0]], data=datapoint.values.dot(weights))

    def weighted_average_linear(datapoint, window, full_data):
        """Takes time weighted average of data frame. Each datapoint is weighted from its start time to the next
        datapoints start time.
        :param datapoint: pd.df/pd.series. index includes the start of the interval and all data is between start and start + interval.
        :param window: int seconds.
        :returns the value in the dataframe weighted by the time duration."""
        datapoint = datapoint.sort_index()
        temp_index = np.array(list(datapoint.index) + [datapoint.index[0] + datetime.timedelta(seconds=window)])

        if isinstance(datapoint, pd.DataFrame):
            temp_values = np.array(
                list(datapoint.values) + [full_data.loc[temp_index[-1]].values])
        else:
            temp_values = np.array(list(datapoint.values) + [full_data.loc[temp_index[-1]]])

        new_values = []
        for i in range(0, len(temp_values)-1):
            new_values.append((temp_values[i+1] + temp_values[i])/2.)

        new_values = np.array(new_values)
        diffs = temp_index[1:] - temp_index[:-1]
        weights = np.array([d.total_seconds() for d in diffs]) / float(window)

        assert 0.99 < sum(weights) < 1.01  # account for tiny precision errors.
        if isinstance(datapoint, pd.DataFrame):
            return pd.DataFrame(index=[datapoint.index[0]], columns=datapoint.columns, data=[new_values.T.dot(weights)])
        else:
            return pd.Series(index=[datapoint.index[0]], data=new_values.dot(weights))

    if method == "interpolate":
        # take weighted average and groupby datapoints which are in the same interval.
        data_grouped = data.iloc[:-1].groupby(by=lambda x: (x - start).total_seconds() // window, group_keys=False).apply(func=lambda x: weighted_average_linear(x, window, data))
    else:
        data_grouped = data.iloc[:-1].groupby(by=lambda x: (x - start).total_seconds() // window, group_keys=False).apply(func=lambda x: weighted_average_constant(x, window))

    return data_grouped


if __name__ == "__main__":
    pass
