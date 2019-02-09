"""Datetime related utility functions"""

from datetime import datetime

import pytz


def utc_timestamp_to_str(timestamp_seconds, utc_offset_seconds, format='%Y-%m-%d'):
    """
    Converts a UTC timestamp to local datetime string based on the given
    timezone offset.

    Args:
        timestamp_seconds (int): UTC timestamp in seconds
        utc_offset_seconds (int): Offset of the target timezone to UTC
            in seconds
        format (str): Defaults to '%Y-%m-%d'. Output date string format

    Returns:
        str: Timestamp converted into date time string.
    """

    local_timestamp = timestamp_seconds + utc_offset_seconds
    result = datetime.utcfromtimestamp(local_timestamp)
    return result.strftime(format)


def parse_str_to_timestamp(datetime_str, utc_offset_seconds, format='%Y-%m-%d'):
    """
    Converts date string in the given format to UTC timestamp (in seconds)
    according to the specified timezone offset.

    Args:
        datetime_str (str): Datetime string.
        utc_offset_seconds (int): Offset of the target timezone to UTC
            in seconds
        format (str): Defaults to '%Y-%m-%d'. Format of `datetime_str`.

    Returns:
        int: Converted timestamp (in seconds)

    Example:
        >>> parse_str_to_timestamp('20190101', 28800, '%Y%m%d')
        >>> 1546272000
    """

    parsed = datetime.strptime(datetime_str, format)
    parsed = parsed.replace(tzinfo=pytz.UTC)
    return int(parsed.timestamp() - utc_offset_seconds)
