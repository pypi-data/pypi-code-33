#!/usr/bin/env python3

from datetime import datetime
import re

import pytz


LOCAL_TZ = pytz.timezone('Europe/Paris')
ISO_FORMAT_TZ = '%Y-%m-%dT%H:%M:%S%z'
ISO_FORMAT_MICRO_TZ = '%Y-%m-%dT%H:%M:%S.%f%z'
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
ISO_FORMAT_MICRO = '%Y-%m-%dT%H:%M:%S.%f'
ISO_FORMATS = [ISO_FORMAT_TZ, ISO_FORMAT_MICRO_TZ, ISO_FORMAT, ISO_FORMAT_MICRO]
HTTP_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'


def now(roundtominute=False):
    date = datetime.now()
    return to_local(date, roundtominute)


def utcnow(roundtominute=False):
    date = datetime.utcnow()
    return to_utc(date, roundtominute)


def from_timestamp(timestamp, roundtominute=False):
    date = datetime.fromtimestamp(timestamp)
    return to_local(date, roundtominute)


def to_local(date, roundtominute=False):
    return to_tz(date, LOCAL_TZ, roundtominute)


def to_utc(date, roundtominute=False):
    return to_tz(date, pytz.utc, roundtominute)


def to_tz(date, tz, roundtominute=False):
    if type(date) is not datetime:
        return None

    try:
        date = tz.localize(date)
    except ValueError:
        date = date.astimezone(tz)
    date = date.replace(microsecond=0)
    if roundtominute:
        date = round_to_minute(date)
    return date


def round_to_minute(date):
    if type(date) is not datetime:
        return None

    return date.replace(second=0)


def to_string(date, strformat=ISO_FORMAT_TZ):
    if type(date) is str:
        return date
    if type(date) is not datetime:
        return None

    return date.strftime(strformat)


def from_string(string, dateformat=None):
    if type(string) is datetime:
        return to_local(string)
    if type(string) is not str:
        return None

    string = re.sub(r'([\+|\-][0-9]{2}):([0-9]{2})$', r'\1\2', string)  # handles .isoformat() output
    dateformats = ISO_FORMATS
    if dateformat is not None:
        dateformats = [dateformat,] + dateformats

    for dateformat in dateformats:
        try:
            date = datetime.strptime(string, dateformat)
        except ValueError:
            pass
        else:
            return to_local(date)

    return None


def to_http_date(date):
    if type(date) is not datetime:
        return None

    return date.strftime(HTTP_FORMAT)
