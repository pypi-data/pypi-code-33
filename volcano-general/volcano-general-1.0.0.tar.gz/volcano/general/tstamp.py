#!/usr/bin/python3


import datetime


def get_current_tstamp_utc() -> datetime.datetime:
    return datetime.datetime.utcnow()


def serialize_tstamp(tstamp_n: (datetime.datetime, None)) -> str:
    assert tstamp_n is None or isinstance(tstamp_n, datetime.datetime), tstamp_n

    return '' if tstamp_n is None else tstamp_n.strftime('%Y-%m-%dT%H:%M:%S.%f')    # %f is microsec, xxxxxx
    # return '' if tstamp_n is None else tstamp_n.isoformat(timespec='milliseconds') -- timespec appeared in 3.6


def deserialize_tstamp_w(s: (str, None)) -> (datetime.datetime, None):
    assert s is None or isinstance(s, str), s

    if not s:
        return None

    try:
        return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%f')    # %f is microsec, xxxxxx
        # return datetime.datetime.fromisoformat(s)  -- from Python 3.7
    except ValueError as e:
        raise Warning('Invalid datetime format: {}'.format(e))
