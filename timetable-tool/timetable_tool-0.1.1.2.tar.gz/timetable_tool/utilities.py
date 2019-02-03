"""This module provides utility modules.

They are for my scraping application and are to uselful for:
- Working with estudent and datetime
- Working with the Google Calendar API
"""

import datetime
from timetable_tool import constants


def to_24h_string(string):
    time = datetime.datetime.strptime(string, '%I:%M%p').time()
    return(time.strftime('%H:%M'))


def estudent_to_datetime(string):
    """Take a date in string form and return a datetime object.
    04-May-2017 -> (2017, 5, 4)
    """
    # datetime.date(2017, 5, 4)
    date = datetime.datetime.strptime(string, '%d-%b-%Y').date()
    return date


def datetime_to_estudent(date):
    """Take a datetime object and return a compatible string.
    (2017, 5, 4) -> 04-May-2017
    """
    string = date.strftime('%d-%b-%Y')
    return string


def date_from_day_abbr(day, date):
    """Calculate date from day name and date in the same week

    Arguments:
    day -- in the form Mon, Tue etc.
    date -- must be from the same week as the 'day'

    Return:
    day_date -- a datetime object
    """
    for i, abbr in enumerate(constants.DAYS):
        if abbr == day:
            if i > date.weekday():
                day_date = date + datetime.timedelta(days=i)
            else:
                day_date = date - datetime.timedelta(days=i)
            break
    return day_date


def to_gcal_datetime(date, time):
    """Convert date and time to google formatted datetime.

    Arguments:
        date -- datetime object
        time -- time string containing the time

    Return:
        gcal_datetime -- formatted date string

    """
    gcal_datetime = '{}-{:>02}-{:>02}T{}:00+08:00'.format(
        date.year, date.month, date.day, time)
    return gcal_datetime
