import pandas
import numpy

from ..points_serializers import NANOSECONDS

DEFAULT_TZ = 'UTC'


def milli_tuple_naive_to_pandas_tz_aware(arr, tz=DEFAULT_TZ):
    """
    Converts an array of points represented as milli+value tuples to localized pandas.Series.
    It\s correctly handles dst transitions avoiding gaps and repeating hours.

    :param arr: Array of points
    :param tz: Name of timezone to localize points into.
    """
    tz = tz or DEFAULT_TZ

    occurrence = set()
    dates, dsts = [], []
    for p in arr:
        dt = p[0]
        dates.append(dt * NANOSECONDS)
        dsts.append(dt not in occurrence)
        occurrence.add(dt)
    index = pandas.to_datetime(dates).tz_localize(tz, ambiguous=numpy.array(dsts))
    res = pandas.Series([p[1] for p in arr], index)

    return res
