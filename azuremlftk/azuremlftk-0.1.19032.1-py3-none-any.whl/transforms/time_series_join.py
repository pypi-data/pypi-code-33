"""
Merge two timeseries
"""
from warnings import warn
import numpy as np
import pandas as pd
idx = pd.IndexSlice

from ftk import TimeSeriesDataFrame

class Interval:
    """
    Represents a time interval.  Pandas version 0.20.3 Interval class does not
    have a length value
    """
    def __init__(self, start:pd.datetime, end:pd.datetime):
        """
        Setup time interval

        :param start:
            Start of interval
        :type start:
            pd.datetime

        :param end:
            End of interval
        :type end:
            pd.datetime
        """
        self.start = start
        self.end = end

    @property
    def length(self):
        """
        Interval length

        :returns: interval length
        :rtype: pd.TimeDelta
        """
        return self.end - self.start

def alloc_uniform(
        values:list,
        src_interval:Interval,
        dst_interval:Interval,
        *args,
        **kwargs):
    """
    Uniformly allocate the ``value`` associated with ``src_interval`` to
    ``dst_interval``.  The ``dst_interval`` must be contained within
    ``src_interval``.

    :param value:
        The data value measured during the ``src_interval``
    :type value:
        number

    :param src_interval:
        The interval distributing (some of) its value to the ``dst_interval``
    :type src_interval:
        Interval

    :param dst_interval:
        The interval being assigned values from that of ``src_interval``
    :type dst_interval:
        Interval

    :param args:
        [Unused] additional user-supplied arguments.
    :type args:
        tuple

    :param kwargs:
        [Unused] additional user-supplied keyword arguments.
    :type kwargs:
        dict

    :returns:
        A value adjusted for ``dst_interval``
    :rtype:
        number
    """
    interval_ratio = dst_interval.length/src_interval.length
    return [value*interval_ratio for value in values]

def alloc_step(
        values:list,
        src_interval:Interval,
        dst_interval:Interval,
        *args,
        **kwargs):
    """
    Copy the ``value`` associated with ``src_interval`` to
    ``dst_interval``.  The ``dst_interval`` must be contained
    within ``src_interval``.

    :param value:
        The data value measured during the ``src_interval``
    :type value:
        number

    :param src_interval:
        The interval distributing (some of) its value to the ``dst_interval``
    :type src_interval:
        Interval

    :param dst_interval:
        The interval being assigned values from that of ``src_interval``
    :type dst_interval:
        Interval

    :param args:
        [Unused] additional user-supplied arguments.
    :type args:
        tuple

    :param kwargs:
        [Unused] additional user-supplied keyword arguments.
    :type kwargs:
        dict

    :returns:
        A value adjusted for ``dst_interval``
    :rtype:
        number
    """
    return values

def agg_sum(
    values:list,
    intervals,
    *args,
    **kwargs):
    """
    Return the sum of the values contained in ``intervals``.

    :param values:
        The values to sum.  This list contains lists of each data value from
        the ``right`` timeseries.
    :type values:
        list(list)

    :param intervals:
        [Unused] intervals associated with values from ``values``
    :type src_interval:
        list(Interval)

    :param args:
        [Unused] additional user-supplied arguments.
    :type args:
        tuple

    :param kwargs:
        [Unused] additional user-supplied keyword arguments.
    :type kwargs:
        dict

    :returns:
        A single list containing the summed values from each data column
    :rtype:
        list
    """
    return [sum(v) for v in values]

def agg_average(
    values:list,
    intervals,
    *args,
    weighted=True,
    **kwargs):
    """
    Return the average of the values contained in ``intervals``.

    :param values:
        The values to sum.  This list contains lists of each data value from
        the ``right`` timeseries.
    :type values:
        list(list)

    :param intervals:
        [Unused] intervals associated with values from ``values``
    :type src_interval:
        list(Interval)

    :param args:
        [Unused] additional user-supplied arguments.
    :type args:
        tuple

    :param weighted:
        Weight values by interval length
    :type weighted:
        bool

    :param kwargs:
        [Unused] additional user-supplied keyword arguments.
    :type kwargs:
        dict

    :returns:
        A single list containing the summed values from each data column
    :rtype:
        list
    """
    if weighted:
        weights = [i.length for i in intervals]
        return [np.average(v, weights=weights) for v in values]
    else:
        return [np.average(v) for v in values]

def get_time(series:pd.Series):
    """
    Get the time index from a pandas ``Series`` object.  When ``<expr>`` in
    ``tsdf.iloc[<expr>]`` is an integer rather than a slice, the returned
    object is a pandas ``Series``, which will store the time index either as
    the first entry in its ``name`` tuple property or will be the ``name``
    property itself when ``tsdf`` has no grains.

    :param series:
        A single-row ``series`` object from which to extract the time value
    :type series:
        pd.series

    :returns:
        The time value from ``series``
    :rtype:
        datetime-like object
    """
    # pd.Series.name is a tuple of index values in the case of multiple indices,
    # so we assume that the user will not have an object of type tuple as the
    # time index
    if isinstance(series.name, tuple):
        return series.name[0]
    else:
        return series.name

def merge_time_series(
        left:TimeSeriesDataFrame,
        right:TimeSeriesDataFrame,
        right_bias:str='start',
        alloc_func:callable=alloc_uniform,
        alloc_args:tuple=None,
        alloc_kwargs:dict=None,
        agg_func:callable=agg_sum,
        agg_args:tuple=None,
        agg_kwargs:dict=None):
    """
    Merge ``right`` time series data frame (TSDF) into ``left`` TSDF.  Merging
    occurs in two stages:

    1. Split intervals from ``right`` at timepoints in ``left`` so that the
       resulting common time series contains all the timepoints from both
       series.  According to ``alloc_func`` split the value from ``right`` into
       the new (smaller) intervals.
    2. Merge the common timeseries intervals so that only the timepoints from
       ``left`` remain and using ``agg_func`` collect the resulting values
       calculated from ``right`` into  corresponding intervals in ``left``.

    The resulting series is an inner join of ``left`` and ``right`` rebased on
    ``left``'s timepoints.

    :param left:
        Destination timeseries
    :type left:
        pandas.DataFrame

    :param right:
        Source timeseries
    :type right:
        pandas.DataFrame

    :param right_bias:
        [TODO: not implemented] Either ``'start'``, ``'mid'``, or ``'end'``.
        Indicates that data in ``right`` timeseries associates with the start,
        end, or halves of its adjacent intervals.  If during timeseries merge
        any of ``right``'s intervals must be split or joined, this parameter
        determines if split values are associated with the start, middle, or
        end timepoints of the new interval configuration.  In the middle case,
        data associated with each timepoint is considered to represent from the
        time 1/2 interval before the timepoint to the time 1/2 interval after.

        Also, this implies that either the first timepoint (``bias ==
        'start'``) or last timepoint (``bias == 'end'``) or both timepoints
        (``bias == 'mid'``) in the series represent(s) data beyond the nominal
        edges of the timeseries by exactly one interval length.
    :type right_bias:
        str

    :param alloc_func:
        Allocator function used to allocate values from ``right`` intervals to
        equal or smaller intervals.
    :type alloc_func:
        pandas.DataFrame

    :param alloc_args:
        Additional arguments to pass to ``alloc_func``.
    :type alloc_args:
        tuple

    :param alloc_kwargs:
        Additional keyword arguments to pass to ``alloc_func``.
    :type alloc_kwargs:
        dict

    :param agg_func:
        Aggregator function used to accumulate values from merged adjacent
        intervals into a single value for the merged interval.
    :type agg_func:
        pandas.DataFrame

    :param agg_args:
        Additional arguments to pass to ``agg_func``.
    :type agg_args:
        tuple

    :param agg_kwargs:
        Additional keyword arguments to pass to ``agg_func``.
    :type agg_kwargs:
        dict

    :returns:
        Merged timeseries with ``right``'s values distributed over ``left``'s
        intervals
    :rtype:
        ftk.TimeSeriesDataFrame
    """
    # Translate immutable argument defaults
    if alloc_args is None:
        alloc_args = ()
    if alloc_kwargs is None:
        alloc_kwargs = {}
    if agg_args is None:
        agg_args = ()
    if agg_kwargs is None:
        agg_kwargs = {}
    # Validate functions
    for func in (alloc_func, agg_func):
        if not callable(func):
            raise TypeError('alloc_func and agg_func must be callable objects')

    # Valdate series
    for series in (left, right):
        # Check type
        if not isinstance(series, TimeSeriesDataFrame):
            raise TypeError('left and right timeseries must be of type'
                             ' ftk.TimeSeriesDataFrame')
        # Check sorted
        if not series.index.is_monotonic_increasing:
            raise ValueError('left and right timeseries must be index sorted in'
                             ' ascending order before merge')
    # Check grains
    common_grains = set(left.grain_colnames or []).intersection(right.grain_colnames or [])
    if len(common_grains) > 0:
        raise ValueError('time_series_join currently only works without grains')
    uncommon_grains = set(left.grain_colnames or []).symmetric_difference(right.grain_colnames or [])
    if uncommon_grains:
        warn('unshared grains {} from left and right will be discarded'
             ''.format(uncommon_grains), UserWarning)
    # Check columns
    common_columns = set(left.columns).intersection(right.columns)
    if common_columns:
        raise ValueError('left and right timeseries both contain columns:'
                         ' {}'.format(common_columns))
    # Check intervals
    if len(left) < 2 or len(right) < 2:
        raise ValueError('left and right timeseries must each have at least'
                         ' two timepoints')

    # Perform time series merge
    split_data = _allocate(left, right, right_bias, alloc_func, alloc_args, alloc_kwargs)
    return _aggregate(split_data, left, right, right_bias, agg_func, agg_args, agg_kwargs)

def _allocate(left, right, right_bias, alloc_func, alloc_args, alloc_kwargs):
    """
    Split intervals from ``right`` at timepoints in ``left``.  Allocate
    ``right``'s values according to ``alloc_func``.
    """
    # Get extrema time pointers
    left_start = get_time(left.iloc[0])
    left_end = get_time(left.iloc[-1])
    right_start = get_time(right.iloc[0])
    right_end = get_time(right.iloc[-1])

    # Store split intervals in intermediate data structure
    split_data = []
    left_i = right_i = 0
    # Offset loop start to common time covering
    if left_start < right_start:
        left_offset = len(left.loc[idx[:right_start], :]) - 1
        if left_offset > 0:
            left_i = left_offset
    elif right_start < left_start:
        right_offset = len(right.loc[idx[:left_start], :]) - 1
        if right_offset > 0:
            right_i = right_offset
    while True:
        # Setup left and right timepoint pointers.  The left and right
        # timepoints below are used to construct the interval objects sent to
        # alloc_func and agg_func
        try:
            curr_left = left.iloc[left_i]
            next_left = left.iloc[left_i + 1]
            curr_right = right.iloc[right_i]
            next_right = right.iloc[right_i + 1]
        except IndexError:
            break  # Iterate each series until one is exhausted

        # The destination interval is defined dependant upon
        # the disposition of the current intervals as shown below
        dst_interval = None
        # Case 1
        # L: -+----+------------
        # R: ----------+------+-
        # Case 2
        # L: ---+----+----------
        # R: --------+------+---
        if get_time(next_left) <= get_time(curr_right):
            left_i += 1
        # Case 3
        # L: ------------+----+-
        # R: -+------+----------
        # Case 4
        # L: ----------+----+---
        # R: ---+------+--------
        elif get_time(curr_left) >= get_time(next_right):
            right_i += 1
        # Case 5
        # L: ----+----+---------
        # R: -------+------+----
        elif get_time(curr_left) < get_time(curr_right) < get_time(next_left) < get_time(next_right):
            dst_interval = Interval(get_time(curr_right), get_time(next_left))
            left_i += 1
        # Case 6
        # L: ---------+----+----
        # R: ----+------+-------
        elif get_time(curr_right) < get_time(curr_left) < get_time(next_right) < get_time(next_left):
            dst_interval = Interval(get_time(curr_left), get_time(next_right))
            right_i += 1
        # Case 7
        # L: -------+--+--------
        # R: -----+-------+-----
        # Case 8
        # L: ------+--+---------
        # R: ------+------+-----
        elif get_time(curr_left) >= get_time(curr_right) and get_time(next_left) < get_time(next_right):
            dst_interval = Interval(get_time(curr_left), get_time(next_left))
            left_i += 1
        # Case 9
        # L: -----+-------+-----
        # R: -------+--+--------
        # Case 10
        # L: ------+------+-----
        # R: ------+--+---------
        elif get_time(curr_left) <= get_time(curr_right) and get_time(next_left) > get_time(next_right):
            dst_interval = Interval(get_time(curr_right), get_time(next_right))
            right_i += 1
        # Case 11
        # L: ----------+--+-----
        # R: ------+------+-----
        # Case 12
        # L: ------+------+-----
        # R: ------+------+-----
        elif get_time(curr_left) >= get_time(curr_right) and get_time(next_left) == get_time(next_right):
            dst_interval = Interval(get_time(curr_left), get_time(next_left))
            left_i += 1
            right_i += 1
        # Case 13
        # L: ------+------+-----
        # R: ----------+--+-----
        elif get_time(curr_left) < get_time(curr_right) and get_time(next_left) == get_time(next_right):
            dst_interval = Interval(get_time(curr_right), get_time(next_right))
            left_i += 1
            right_i += 1

        if dst_interval:
            # Calculated needed data
            src_interval = Interval(get_time(curr_right), get_time(next_right))
            # The left values only appear at left timepoints in the combined
            # list of timepoints, but the prevailing right values will be
            # modified by alloc_func for each timepoint until the next right
            # timepoint is found
            left_values = None if get_time(curr_left) < get_time(curr_right) else curr_left.values
            right_values = curr_right.values
            dst_values = alloc_func(right_values, src_interval, dst_interval, *alloc_args, **alloc_kwargs)

            # Append data to list
            split_data.append({
                'interval': dst_interval,
                'left_values': left_values,
                'right_values': dst_values,
            })

    return split_data

def _aggregate(split_data, left, right, right_bias, agg_func, agg_args, agg_kwargs):
    """
    Join intervals in ``split_data`` that do not begin/end at timepoints in
    ``left``.  Aggregate values from ``right`` according to ``agg_func``.
    """
    # Add merged intervals from right into left
    combined_data = {left.time_colname: []}
    #combined_data.update({grain_col: [] for grain_col in common_grains})
    combined_data.update({value_col: [] for value_col in list(left.columns) + list(right.columns)})
    # If intersection is empty, return empty data frame
    if len(split_data) == 0:
        return pd.DataFrame(combined_data)

    # TODO: fix first/last case handling when implementing bias parameter
    # First case
    if split_data[0]['left_values'] is not None:
        combined_data[left.time_colname].append(split_data[0]['interval'].start)
        for i, colname in enumerate(left.columns):
            combined_data[colname].append(split_data[0]['left_values'][i])
        right_values = [split_data[0]['right_values']]
        right_intervals = [split_data[0]['interval']]
    else:
        right_values = []
        right_intervals = []
    # Middle case
    for row in split_data[1:]:
        # Collect right data
        if row['left_values'] is None:
            right_values.append(row['right_values'])
            right_intervals.append(row['interval'])
        # Found left timepoint
        else:
            # Aggregate right data
            if right_values:
                combined_values = agg_func(np.transpose(right_values), right_intervals, *agg_args, **agg_kwargs)
                combined_data[left.time_colname].append(row['interval'].start)
                for i, colname in enumerate(left.columns):
                    combined_data[colname].append(row['left_values'][i])
                for i, colname in enumerate(right.columns):
                    combined_data[colname].append(combined_values[i])
                right_values = [row['right_values']]
                right_intervals = [row['interval']]
    # Last case
    else:
        if split_data[-1]['right_values'] is not None:
            for i, colname in enumerate(right.columns):
                # TODO: fix when implementing bias parameter
                if len(combined_data[left.time_colname]) > len(combined_data[colname]):
                    right_values = [split_data[-1]['right_values']]
                    right_intervals = [split_data[-1]['interval']]
                    combined_values = agg_func(np.transpose(right_values), right_intervals, *agg_args, **agg_kwargs)
                    combined_data[colname].append(combined_values[i])

    return TimeSeriesDataFrame(pd.DataFrame(combined_data),
                               time_colname=left.time_colname,
                               grain_colnames=None)
