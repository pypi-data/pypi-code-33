""" Utilities for time series and dates. """
import pandas as pd
import calendar


def groupby_yday(df):
    """ Groups a pandas DataFrame by the day of year.

    :param: df: A pandas DataFrame.

    :returns: The grouped DataFrame.
    """
    return df.groupby(lambda d: d.timetuple().tm_yday)


def groupby_month(df):
    """ Groups a pandas DataFrame by month.

    :param: df: A pandas DataFrame.

    :returns: The grouped DataFrame.
    """
    return df.groupby(df.index.month)


def groupby_year_month(df):
    """ Groups a pandas DataFrame by year and month.

    :param: df: A pandas DataFrame.

    :returns: The grouped DataFrame.
    """
    return pd.groupby(df, by=[df.index.year, df.index.month])


def short_month(i, zero_based=False):
    """ Looks up the short name of a month with an index.

    :param: i: Index of the month to lookup.
    :param: zero_based: Indicates whether the index starts from 0.

    :returns: The short name of the month for example Jan.
    """
    j = i

    if zero_based:
        if i < 0 or i > 11:
            raise AssertionError("Out of range " + i)

        j = i + 1

    return calendar.month_abbr[j]


def short_months():
    """ Gets the short names of the months.

    :returns: A list containing the short month names.
    """
    return [short_month(i) for i in range(13)]


def month_index(month, zero_based=False):
    """ Looks up the index of a month from a short name.

    :param: i: The short name of a month to lookup for example Jan.
    :param: zero_based: Indicates whether the index starts from 0.

    :returns: The index of the month.
    """
    for i, m in enumerate(short_months()):
        if m == month:
            index = i

            if not zero_based:
                index += 1

            return i
