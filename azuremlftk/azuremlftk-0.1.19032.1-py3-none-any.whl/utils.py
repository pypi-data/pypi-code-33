"""
A module that provides generic utility functions that could be useful to all classes in AML forecasting package.
"""

import numpy as np
import pandas as pd
from warnings import warn
import subprocess
from collections import defaultdict
from ftk.verify import is_iterable_but_not_string, istype, is_list_oftype
from ftk.exception import (AzureMLForecastException, 
                           DataFrameMissingColumnException)
import sys
import importlib

### NOTE:
# Do not import TimeSeriesDataFrame or ForecastDataFrame at the top of this 
# file, because both of them import this file as well, and circular references
# emerge. It is ok to import TSDF or FDF inside a function instead.
###


def iterfn(n, f, x):
    """
    Iterate a single-argument function f for n number of times, such that an
    initial input to the function f is an argument x whereas successfive
    invocations of f operate on the output of previous invocation of f.
    For example, iterfn(4,f,x) = f(f(f(f(x)))).

    :param n:
        Number of times the operation (f) needs to be performed iteratively.
    :param f:
        A function that needs to be called.
    :param x:
        An argument to be passed to the input function f.
    :return:
        Result of applying the function f iteratively for n number of times.

    """    
    assert (isinstance(n, int));
    assert (n >= 0);
    assert (callable(f));

    if n == 0:
        return x
    
    return f(iterfn(n-1,f,x))


def get_period_offsets_from_dates(reference_index, time_index, freq,
                                  misalignment_action='warn'):
        """
        Determine the integer offsets of time_index
        from the reference index values in number of periods.
        Periods are defined with respect to the time series
        frequency.

        :param reference_index: 
            Baseline from which to compute offsets
        :type reference_index: pd.DatetimeIndex, pd.Timestamp
        :param time_index: timedate values
        :type time_index: pd.DatetimeIndex
        :param freq: Time series frequency
        :type freq: str (offset alias), pd.DateOffset
        :param misalignment_action: 
            Action to perform if the time/reference indices are misaligned with 
            respect to the given frequency. 
            Possible actions are 'warn' and 'error'
        :type misalignment_action: str
        :return: 
            numpy array of integer offsets with same length as time_index
        :rtype: numpy.ndarray

        Example:
        >>> time_index = pd.date_range(start='2017-04', periods=6, freq='MS')
        >>> time_index
        DatetimeIndex(['2017-04-01', '2017-05-01', '2017-06-01', '2017-07-01',
                        '2017-08-01', '2017-09-01'],
                        dtype='datetime64[ns]', freq='MS')
        >>> get_period_offsets_from_dates(pd.Timestamp('2017-03'), 
        ...                               time_index, freq='MS')
        array([1, 2, 3, 4, 5, 6], dtype=int64)

        """

        if freq is None:
            error_message = \
                ('get_period_offsets_from_dates: Cannot find ' + 
                'period offsets. Time series frequency is not set.')
            raise AzureMLForecastException(error_message)

        if is_iterable_but_not_string(reference_index):
            if len(reference_index) != len(time_index):
                raise AzureMLForecastException(
                    ('reference_index ({0}) and time_index ({1}) ' +
                     'must be the same length').format(
                        len(reference_index), len(time_index)))

        else:
            # Make an index with same length as time index 
            #  by recycling the given value
            reference_index = pd.DatetimeIndex(np.repeat(reference_index, 
                                                         len(time_index)))

        # Construct a regular grid of dates to define 
        #  the set of possible horizons
        min_date = min(time_index.min(), reference_index.min())
        max_date = max(time_index.max(), reference_index.max())
        date_grid = pd.date_range(start=min_date, end=max_date, freq=freq)

        # Check for mis-alignment of references and time indices
        if any(ref not in date_grid for ref in reference_index):
            msg = ('get_period_offsets_from_dates: ' +
                   'Reference dates are misaligned. ' +
                   'Expected dates on grid {0}').format(date_grid)
            if misalignment_action == 'warn':
                warn(msg, UserWarning)
            else:
                raise AzureMLForecastException(msg)
        
        if any(dt not in date_grid for dt in time_index):
            msg = ('get_period_offsets_from_dates: ' +
                   'Time index dates are misaligned. ' +
                   'Expected dates on grid {0}').format(date_grid)
            if misalignment_action == 'warn':
                warn(msg, UserWarning)
            else:
                raise AzureMLForecastException(msg)

        #  Helper functions for making a lookup table and finding the
        #  horizon/offset for a given date.
        # A lookup table for offsets is necessary here because the date grid
        #   may not have uniform spacing with respect to fixed time intervals
        #   like days and hours. Hence, vectorized arithmetic won't always
        #   work when finding the correct offsets.
        #   A classic example of this case is if the time series frequency is
        #   quarterly. Some quarters are 90 days, some are 92 days, etc.
        #   Even more egregious case would be a "Work Day" frequency with gaps
        #   for weekends and holidays.
        def make_lookup(ref_date):
            """
            Make a horizon lookup table relative to a given reference date.
            The lookup is the map: datetime -> integer offset/horizon
            """        

            # Find the index of the grid point closest to the reference date
            # This point is defined as horizon 0
            grid_diff = date_grid - ref_date
            zero_idx = np.argmin(np.abs(grid_diff.values))

            # Assign integer horizons/offsets to each grid point
            horizons = np.arange(-1*zero_idx, -1*zero_idx + len(date_grid))
            return dict(zip(date_grid, horizons))

        def find_horizon(dt, horizon_lookup):
            """
            Find the horizon corresponding to datetime (dt)
            using the given lookup table
            """

            # Find the index of the closest grid point to the input date
            date_diff = dt - date_grid
            closest_idx = np.argmin(np.abs(date_diff.values))

            # Lookup the offset via the closest grid point
            return horizon_lookup[date_grid[closest_idx]]

        # Make lookup tables for each unique reference date
        lookups = {ref_date: make_lookup(ref_date) 
                   for ref_date in reference_index.unique()}
        
        horizons = [find_horizon(dt, lookups[ref])
                    for dt, ref in zip(time_index, reference_index)]
        
        return np.array(horizons)

def grain_level_to_dict(grain_colnames, grain_level):
    """
    Convert a grain level to a dictionary where the keys
    are given by grain_colnames.
    The grain_level parameter is generally derived from
    the 'name' property of a pd.DataFrame.GroupBy.
    That is, 
    for name, group in X.groupby(level=X.grain_colnames):
       print('grain_level is {}'.name)

    :Example:
     >>> _grain_level_to_dict(['store', 'brand'], ('walmart', 'nike'))
     {'brand': 'nike', 'store': 'walmart'}

    """

    gr = grain_level
    if not is_iterable_but_not_string(gr):
        gr = (gr,)

    gr_colnames = grain_colnames
    if not is_iterable_but_not_string(gr_colnames):
        gr_colnames = [gr_colnames]

    return dict(zip(gr_colnames, gr))

def make_groupby_map(df, groupby_cols_or_indices):
    """
    Utility function for creating a groupby map for a data frame when the 
    items defining the groups may be in the index, the regular column set, 
    or both.

    This function returns a pandas Series object with the same index as df
    while the values are group identifiers (as scalars or tuples).
    The returned Series can be passed directly to pd.DataFrame.groupby
    as the "by" argument; pandas interprets the series as a mapping from
    index values to groups. 

    As of Pandas 0.20.3, pd.DataFrame.groupby does not have a unified 
    interface for the use case of grouping by items in the index, the columns, 
    or both. This function should only be used if you need this general 
    functionality. If you know that your groupby items are definitely
    in the columns or the index, use normal pandas groupby(by=<columns>) 
    or groupby(level=<indices>), respectively. This utility is much less
    performant than straight groupby in those cases. 
    """
   
    if groupby_cols_or_indices is None \
        or len(groupby_cols_or_indices) == 0:
        from ftk import TimeSeriesDataFrame
        # Return an identity mapping when there are no groupby columns
        return pd.Series(TimeSeriesDataFrame.identity_grain_level(), 
                         index=df.index)

    if not is_iterable_but_not_string(groupby_cols_or_indices):
        groupby_cols_or_indices = [groupby_cols_or_indices]

    # Internal function for column/index value extraction
    # ------------------------------------------------------
    def get_col_or_index(colname):
        if colname in df.columns:
            return df[colname].values
        elif colname in df.index.names:
            return df.index.get_level_values(colname)
        else:
            raise DataFrameMissingColumnException(
                'Column does not exist: {0}'.format(colname))
    # ------------------------------------------------------

    # Make a helper dataframe with a copy of df's index
    #  and columns containing only the groupby columns from df
    helper_dict = {'gby_' + col: get_col_or_index(col) 
                    for col in groupby_cols_or_indices}
    helper_df = pd.DataFrame(helper_dict, index=df.index)
    groupby_cols = ['gby_' + col for col in groupby_cols_or_indices]

    # Condense the helper dataframe to a Series where each value
    #  is a scalar (for one groupby columns) or a tuple (multiple columns)
    if len(groupby_cols) == 1:
        series_map = helper_df[groupby_cols[0]]
    else:
        series_map = pd.Series(
            map(tuple, helper_df[groupby_cols].values), 
            index=helper_df.index)

    return series_map


def convert_to_list(data):
    """
    If data is not a list, convert it to a list and return the list.

    :param data: input data of any type that can be converted to list.

    :return:
        A list converted from input ``data`` if ``data`` is not a list. 
        Otherwise returns ``data``.
    """
    if is_iterable_but_not_string(data):
        if not isinstance(data, list):
            return list(data)
        else:
            return data
    else:
        return [data]


def get_os():
    """
    Return the operating system of the host machine.

    :return:
        One of these values: "windows", "linux", and "others".
    """
    import sys
    os_name = sys.platform
    if os_name.startswith("win"):
        return "windows"
    elif os_name == "linux":
        return "linux"
    else:
        return "others"


def run_shell(command_as_list):
    """
    Run the shell command.
    
    :param command_as_list: Command formulated as a list of strings.
    :type command_as_list: List of string.
    
    :return:
        A CompletedProcess instance. If there is an execution service error 
        then it raises CalledProcessError.
    
    :example:
    >>> run_shell(["pwd"])
    """
    shell = False if get_os() == "linux" else True
    completed_process = subprocess.run(command_as_list, stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       universal_newlines=True, shell=shell)
    out, err = completed_process.stdout, completed_process.stderr
    return out, err


def run_shell_with_interactive_args(command_as_list, interactive_arg_list):
    """
    Run the shell command with user-provided list of arguments.
    
    :param command_as_list: 
        Command formulated as a list of strings.
    :type command_as_list:
        List of strings.
    
    :param interactive_arg_list:
        List of interactive arguments to the command.
    :type interactive_arg_list:
        List of strings.
    
    :return:
        A CompletedProcess instance. If there is an execution service error 
        then it raises CalledProcessError.
    """
    shell = False if get_os() == "linux" else True
    proc = subprocess.Popen(command_as_list, shell=shell, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                            universal_newlines=True)
    argument_str = '\n'.join(interactive_arg_list)
    out, err = proc.communicate(argument_str)
    return out, err


def flatten_list(input_list):
    """
    Flatten an input list which can have multiple nested lists as items 
    into a single list.
    
    :param input_list:
        A list which can have items of any type.
    
    :return:
        An instance of a generator class from which flattened list can 
        be obtained.
    """
    for item in input_list:
        if is_iterable_but_not_string(item):
            for i in flatten_list(item):
                yield i
        else:
            yield item


def _range(x):
    """Returns the range of a numeric vector, aka (max - min)"""
    return np.max(x) - np.min(x)


def subtract_list_from_list(minuend, subtrahend):
    """
    Compute the difference operation on lists. This is needed whenever 
    order of arguments is important and lists may have duplicates.

    :param minuend:
        List from which subtraction is performed, i.e. ``x`` in expression 
        ``x - y``.
    :type minuend:
        List of any data type.
    :param subtrahend:
        List which is being subtracted, i.e. ``y`` in expression ``x - y``.
    :type subtrahend:
        List of any data type.
    :return: 
        list ``z`` that has all elements of ``minuend`` that are not contained
        in the ``subtrahend``.
    """
    # check types
    istype(minuend, list)
    istype(subtrahend, list)
    result = [x for x in minuend if x not in subtrahend]
    return result


def invert_dict_of_lists(dictionary):
    """
    Given a dictionary of string keys and list values, constructs a reverse dictionary,
    where elements of lists are keys, and initial keys are put into lists in values.

    :param dictionary: 
        Dictionary, that is expected to have strings in keys, and either ints
        or list of ints in values.
    :type dictionary: dict

    :return:
        Inverted dictionary.

    :example:
    >>> input = {'a': [1, 2], 'b': 1, 'c': [0, 2]}
    >>> ouput = invert_dict_of_lists(input)
    >>> output
    >>> {0: ['c'], 1: ['b', 'a'], 2: ['c', 'a']}
    """
   
    if not isinstance(dictionary, dict):
        raise ValueError('Input must be a dictionary!')
    reverse_dict = defaultdict(lambda: []) # default value is empty list
    for key, list_of_values in dictionary.items():
        if not isinstance(list_of_values, list):
            list_of_values = [list_of_values]
        for value in list_of_values:
            reverse_dict[value].append(key)
    return dict(reverse_dict)


def make_repeated_list_strings_unique(x):
    """
    For a list of strings that may have duplicates, returns a list of 
    same length, where each duplicate string gets appended by _i, where
    i starts with 0 and runs sequentially.

    :param x: List of strings.

    :return: 
        List of strings identical in length to an input list with all 
        entries being unique.    
    """
    is_list_oftype(x, str)
    result = x.copy()
    for elem in result:
        num_occurs = result.count(elem)
        # if have duplicates
        if num_occurs > 1:
            # reset duplicates counter
            instance = 0
            for element in result:
                # new name is just 'x_0' or similar
                new_name = element + "_" + str(instance)
                # find first instance of duplicated entry
                if element == elem:
                    # get inside the k-th element of result and replace it
                    result[result.index(element)] = new_name
                    instance += 1
    return result


def standard_deviation_zero_mean(vals):
    """
    Compute standard deviation of a set of values assuming that mean is zero.
    If there are any missing values in the set, those are removed prior 
    to the computation of standard deviation.
    
    :param val:
        List of numbers to compute the standard deviation of.
    :type val:
        List of numerical values.
    
    :return:
        Standard deviation of the numbers in the input list.
    """
    vals = [v for v in vals if not v is None]
    return np.sqrt(np.nanmean(np.power(vals, 2)))


def array_equal_with_nans(x, y):
    """
    Testing for numpy array equality when np.nan are present.
    Standard behavior is np.nan != np.nan, which is correct. However,
    it makes unit testing harder, hence this function.
    :param x:
        A numpy array.
    :type x:
        numpy.ndarray.
    :param y:
        A numpy array.
    :type y:
        numpy.ndarray.
    :return: 
        A boolean indicating if the input arrays are equal or not.
    """
    try:
        np.testing.assert_equal(x, y)
    except AssertionError:
        return False
    return True


def tick_formatter(x, pos):
    if abs(x) >= 1000000:
        #{:1.0f}: show at least one character in total and zero 
        # after the decimal point
        return '{:1.0f}M'.format(x * 1e-6)
    elif abs(x) >= 1000:
        return '{:1.0f}K'.format(x * 1e-3)
    else:
        return '{:1.0f}'.format(x)

def get_matplotlib_attr(package, name, renderer='agg'):
    """
    Return the attribute from package.
    
    :param package: The name of the package, for example matplotlib.ticker.
    :type package: str
    :param name: the name of the class.
    :type name: str
    :param renderer: The renderer name. If renderer is None, it will not be set.
    :type renderer: str
    
    :returns: The class named by literal.
    
    """
    
    module = importlib.import_module(package)
    if hasattr(module, name):
        #Return class/attrubute inside the module.
        return getattr(module, name)
    #import module.
    return importlib.import_module(".".join([package, name]))

def import_plot_and_formatter(renderer='agg'):
    """
    Return matplotlib pyplot and FuncFormatter as a tuple
    
    :returns: a tuple of modules
    :rtype: tuple
    :param renderer: The renderer name. If renderer is None, it will not be set.
    :type renderer: str
    
    """

    from matplotlib import pyplot as plt
    from matplotlib.ticker import FuncFormatter
    return (plt, FuncFormatter)
