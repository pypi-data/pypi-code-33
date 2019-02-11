"""Suite of functions for validating sanity of data."""
import errno
import os
import datetime
import numpy as np
import pandas as pd
from collections import Counter, Iterable
from warnings import warn

from .forecasting_exception import (DataFrameMissingColumnException,
                                    NotSupportedException)

ALLOWED_TIME_COLUMN_TYPES = [pd.Timestamp, pd.DatetimeIndex, pd.Period,
                             pd.PeriodIndex, datetime.datetime, datetime.date]


class Messages:
    """Define validation and error messages."""

    INVALID_TIMESERIESDATAFRAME = "The input X is not a TimeSeriesDataFrame."
    INPUT_IS_NOT_TIMESERIESDATAFRAME = ("Input argument should be an " +
                                        "instance of TimeSeriesDataFrame class.")
    XFORM_INPUT_IS_NOT_TIMESERIESDATAFRAME = ("Transform input should be an " +
                                              "instance of TimeSeriesDataFrame.")
    BAD_MODEL_STATE_MESSAGE = "Model not yet fit"
    SCHEMA_MISMATCH_MESSAGE = ("Schema of the given dataset does not match " +
                               "the expected schema")
    ESTIMATOR_NOT_SUPPORTED = "Estimator is not of supported type."
    PIPELINE_EXECUTION_TYPE_INVALID = ("The execution type specified is " +
                                       "invalid or not supported.")
    PIPELINE_FINAL_ESTIMATOR_INVALID = ("The final estimator in the pipeline " +
                                        "is invalid.")
    PIPELINE_FORMAT_ERROR = ("Pipeline can have transformers with an ending " +
                             "estimator")
    PIPELINE_STEP_ADD_INVALID = "Pipeline validation fails with the new step."
    PIPELINE_STEP_REMOVE_INVALID = "Pipeline step cannot be removed, " \
                                   "because it doesn't exist."
    PIPELINE_EXECUTION_ERROR = "Error executing pipeline."
    PIPELINE_INVALID = "Invalid pipeline"
    COMPUTE_STRATEGY_INVALID = "Compute strategy is either invalid or not set."
    COMPUTE_STRATEGY_MUST_INHERIT_BASE = \
        "Compute strategy is invalid. The compute type must be a subclass of ComputeBase class."
    COMPUTE_ERROR_STATE_INVALID = \
        "Cannot schedule jobs since compute state is invalid. View the errors on the compute object for detail."
    COMPUTE_MUST_IMPLEMENT_EXECUTE_JOB = "A valid 'execute_job' implementation must be provided."
    JOB_TYPE_IS_INVALID = "A valid job type must be specified. Must be one of ftk.factor_types.ComputeJobType."
    JOB_TYPE_NOT_SUPPORTED = "Job type {} is not supported by this compute backend."
    FUNC_PARAM_NOT_SPECIFIED = "A valid processing function parameter must be specified."
    PARAM_MUST_BE_CALLABLE = "The `{}` parameter must be a callable."
    DATA_PARAM_NOT_SPECIFIED = "A valid data parameter must be specified."
    MAPPER_FUNC_PARAM_NOT_SPECIFIED = "A valid data mapper function parameter must be specified."
    SCHEDULER_INVALID = "Scheduler must be an instance of the ftk.compute.scheduler"
    EXECUTE_TASK_JOB_NOT_SUPPORTED = "This compute backend does not support task jobs. " \
        "Use a compute backend that supports executing such jobs."


def get_non_unique(list_in):
    """
    Return the list of values from the given list that are not unique.

    An an empty list is returned if there are no such values.

    :param list_in: The list in which to find non-unique values
    :return: A list of values that are not unique
    """
    ret = [key for key, value in Counter(list_in).items() if value > 1]
    return ret


def type_is_numeric(data_type, message):
    """
    Raise exception if input type is not numeric.

    :param data_type: Input type to test
    :param message: Name of variable being checked
    """
    if not (np.issubdtype(data_type, np.float) or
            np.issubdtype(data_type, np.int) or
            np.issubdtype(data_type, np.uint8) or
            np.issubdtype(data_type, np.int16) or
            np.issubdtype(data_type, np.int32) or
            np.issubdtype(data_type, np.int64)):
        raise ValueError('{0} must be of type int or float'.format(message))


def value_is_int(value, message):
    """
    Raise exception if input type is not integer.

    :param data_type: Input type to test
    :param message: Name of variable being checked
    """
    if not (np.issubdtype(type(value), np.int) or
            np.issubdtype(type(value), np.uint8) or
            np.issubdtype(type(value), np.int16) or
            np.issubdtype(type(value), np.int32) or
            np.issubdtype(type(value), np.int64)):
        raise ValueError('{0} must be of type int'.format(message))


def value_is_string(value, message):
    """
    Raise exception if input type is not string.

    :param data_type: Input type to test
    :param message: Name of variable being checked
    """
    if isinstance(value, str):
        raise ValueError('{0} must be of type str'.format(message))


def type_is_one_of(data_type, given_types, message):
    """
    Raise exception if input type is among a list of given types.

    :param data_type: Input type to test
    :param given_types: List of types to check against
    :param message: Name of variable being checked
    """
    if not any([np.issubdtype(data_type, x) for x in given_types]):
        error_message = (
            '{0} must be one of the following types:'.format(message) +
            '{0}'.format(", ".join([str(x) for x in given_types])))
        raise ValueError(error_message)


def not_none(value, message):
    """
    Raise exception if input value is None.

    :param value: Input value to test
    :param message: Message to output if exception is raised
    """
    if value is None:
        raise ValueError('{0}. Value cannot be Null'.format(message))


def not_none_or_empty(value, message):
    """
    Raise exception if input value is None or empty.

    :param value: Input value to test
    :param message: Message to output if exception is raised
    """
    if value is None or len(value) == 0:
        raise ValueError('{0}. Value is none or empty'.format(message))


def true(value, message):
    """
    Raise exception if input value evaluates to False.

    :param value: Input value to test
    :param message: Message to output if exception is raised
    """
    if not value:
        raise ValueError(message)


def false(value, message):
    """
    Raise exception if input value evaluates to True.

    :param value: Input value to test
    :param message: Message to output if exception is raised
    """
    if value:
        raise ValueError(message)


def not_longerthan(value, maxlen, message):
    """
    Raise exception if input value is longer than a max length.

    :param value: Input value to test
    :param maxlen: Maximum allowed length
    :param message: Message to output if exception is raised
    """
    if len(value) > maxlen:
        raise ValueError('{0}. Length must be < {1}'.format(message, maxlen))


def equals(val1, val2, message):
    """
    Raise exception if input values are not equal.

    :param val1: First input value to test
    :param val2: Second input value to test
    :param message: Message to output if exception is raised
    """
    if val1 != val2:
        raise ValueError("{}. {} must be equal to {}".format(message, val1,
                                                             val2))


def greaterthanzero(value, message):
    """
    Raise exception if input value is less than zero.

    :param value: Input value to test
    :param message: Message to output if exception is raised
    """
    if value <= 0:
        raise ValueError('{0}. Value must be > 0'.format(message))


def greaterthanone(value, message):
    """
    Raise exception if input value is less than one.

    :param value: Input value to test
    :param message: Message to output if exception is raised
    """
    if value <= 1:
        raise ValueError('{0}. Value must be > 0'.format(message))


def lessthan(value, minval, message):
    """
    Raise exception if input value is less than a given minimum.

    :param value: Input value to test
    :param minval: Minimum vlue to check against
    :param message: Message to output if exception is raised
    """
    if value >= minval:
        raise ValueError('{0}. Value must be < {1}'.format(message, minval))


def lessthanequals(value, minval, message):
    """
    Raise exception if input value is less than or equal to a given minimum.

    :param value: Input value to test
    :param minval: Minimum value to check against
    :param message: Message to output if exception is raised
    """
    if value > minval:
        raise ValueError('{0}. Value must be <= {1}'.format(message, minval))


def greaterthan(value, maxval, message):
    """
    Raise exception if input value is greater than a given maximum.

    :param value: Input value to test
    :param maxval: Maximum value to check against
    :param message: Message to output if exception is raised
    """
    if value <= maxval:
        raise ValueError('{0}. Value must be > {1}'.format(message, maxval))


def greaterthanequals(value, maxval, message):
    """
    Raise exception if input value is greater than or equal to a given maximum.

    :param value: Input value to test
    :param maxval: Maximum value to check against
    :param message: Message to output if exception is raised
    """
    if value < maxval:
        raise ValueError('{0}. Value must be >= {1}'.format(message, maxval))


def inrange(value, minval, maxval, message):
    """
    Raise exception if input value is outside of the given range.

    :param value: Input value to test
    :param minval: Minimum value in the range
    :param maxval: Maximum value in the range
    :param message: Message to output if exception is raised
    """
    if value < minval or value > maxval:
        raise ValueError('{0}. Value must be in range: {1}:{2}'.format(
            message, minval, maxval))


def iterable(value):
    """
    Raise exception if input value is not iterable.

    :param value: Input value to test
    """
    not_none(value, "iterable")


def is_list_oftype(value, valuetype):
    """
    Raise exception if input value is not a list of a given type.

    :param value: Input list to test
    :param valuetype: Value type to check against
    """
    if not isinstance(value, list):
        raise ValueError('Must be of type {0}'.format(list))

    if any([not isinstance(x, valuetype) for x in value]):
        raise ValueError('All list elements must be of type {0}'.format(
            valuetype))


def is_iterable_oftype(value, valuetype):
    """
    Raise exception if input value is not an iterable of a given type.

    :param value: Input list to test
    :param valuetype: Value type to check against
    """
    if not is_iterable_but_not_string(value):
        raise TypeError('Value must be iterable.')

    if any([not isinstance(x, valuetype) for x in value]):
        raise TypeError('All elements must be of type {0}'.format(valuetype))


def series_is_numeric(series, message):
    """
    Raise exception if input series is not numeric.

    :param series: Input series to test
    :type series: pd.Series
    :param message: Message to output if exception is raised
    """
    type_is_numeric(series.dtype, message)


def dataframe_is_numeric(dataframe, message):
    """
    Raise exception if input data frame is not numeric.

    :param dataframe: Input frame to test
    :type dataframe: pd.DataFrame
    :param message: Message to output if exception is raised
    """
    for column in dataframe:
        series_is_numeric(dataframe[column], message + "(column {0})".format(
            column))


def dataframe_contains_col(dataframe, column_name, message):
    """
    Raise exception if input data frame does contain a given column.

    :param dataframe: Input frame to test
    :type dataframe: pd.DataFrame
    :param column_name: Column name to check for
    :param message: Message to output if exception is raised
    """
    if column_name not in dataframe:
        raise ValueError('Dataframe {0} does not contain column {1}'.format(
            message, column_name))


def dataframe_contains_index(dataframe, index_name, message):
    """
    Raise exception if input data frame does contain a given index column.

    :param dataframe: Input frame to test
    :type dataframe: pd.DataFrame
    :param index_name: Index column name to check for
    :param message: Message to output if exception is raised
    """
    if index_name not in dataframe.index.names:
        raise ValueError('Dataframe {0} does not contain index {1}'.format(
            message, index_name))


def dataframe_contains_col_index(dataframe, name, message):
    """
    Raise exception if input data frame does contain a given column or index.

    :param dataframe: Input frame to test
    :type dataframe: pd.DataFrame
    :param name: Column or index name to check for
    :param message: Message to output if exception is raised
    """
    if not (name in dataframe.index.names or name in dataframe):
        error_message = ('Dataframe {0} does not contain '.format(message) +
                         'column or index {0}'.format(name))
        raise ValueError(error_message)


def list_contains_value(list_in, value, message):
    """
    Raise exception if input list does not contain a given value.

    :param list_in: Input list to test
    :param value: Value to check
    :param message: Message to output if exception is raised
    """
    if value not in list_in:
        raise ValueError('{0} does not contain {1}'.format(message, value))


def set_contains_value(set_in, value, message):
    """
    Raise exception if input set does not contain a given value.

    :param set_in: Input set to test
    :param value: Value to check
    :param message: Message to output if exception is raised
    """
    if value not in set_in:
        raise ValueError('{0} does not contain {1}'.format(message, value))


def set_does_not_contain_value(set_in, value, message):
    """
    Raise exception if input set contains a given value.

    :param set_in: Input set to test
    :param value: Value to check
    :param message: Message to output if exception is raised
    """
    if value in set_in:
        raise ValueError('{0} contains {1}'.format(message, value))


def series_groupby_is_numeric(series_groupby, message):
    """
    Raise exception if input series groupby object is not numeric.

    :param series_groupby: Input object to test
    :type series_groupby: pd.Series.GroupBy
    :param message: Message to output if exception is raised
    """
    if len(series_groupby) == 0:
        return
    type_is_numeric(series_groupby.dtype.values[0], message)


def directoryexists(value):
    """
    Raise exception if input value is not an existing directory.

    :param value: Directory path to check
    """
    if not os.path.exists(value):
        raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR),
                                 value)


def fileexists(value):
    """
    Raise exception if input value is not an existing file.

    :param value: File path to check
    """
    if not os.path.exists(value):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), value)


def unique_values(value, message):
    """
    Raise exception if input iterable has duplicate values.

    :param value: Input iterable to check
    :param message: Message to output if exception is raised
    """
    non_unique = get_non_unique(value)
    if non_unique is None or len(non_unique) > 0:
        raise ValueError("{0} {1} not unique".format(
            message, ", ".join(non_unique)))


def length_equals(input_list, length, message):
    """
    Raise exception if input list does not have a given length.

    :param value: Input list to check
    :param length: Length to check against
    :param message: Message to output if exception is raised
    """
    if not len(input_list) == length:
        raise ValueError("{0} not of length {1}".format(message, length))


def in_good_state(value, message):
    """
    Raise exception if input evaluates to False.

    :param value: Input object to check
    :param message: Message to output if exception is raised
    """
    if not value:
        raise RuntimeError(message)


def issubclassof(target, base):
    """
    Raise exception if input is not a sub-class of a given base type.

    :param target: Input type to check
    :param base: Base type to check against
    """
    if not issubclass(target, base):
        raise ValueError('{0} must be of subclass of {1}'.format(target, base))


def is_iterable_but_not_string(obj):
    """
    Determine if an object has iterable, list-like properties.

    Importantly, this functions *does not* consider a string
    to be list-like, even though Python strings are iterable.

    :param obj: Object to check
    :return: True if object is iterable
    """
    return isinstance(obj, Iterable) and not isinstance(obj, str)


def data_frame_properties_are_equal(property1, property2):
    """
    Determine if two TimeSeriesDataFrame properties are equal.

    Since the properties can be scalars or vectors, this check is more than
    just a single boolean statement.

    :param property1: First property to check
    :param property2: Second property to check
    :return: True if properties are equal
    """
    p1_iterable = is_iterable_but_not_string(property1)
    p2_iterable = is_iterable_but_not_string(property2)

    if p1_iterable and p2_iterable:
        return set(property1) == set(property2)
    elif (not p1_iterable) and (not p2_iterable):
        return property1 == property2
    elif p1_iterable and (not p2_iterable) and len(property1) == 1:
        return property2 in property1
    elif (not p1_iterable) and p2_iterable and len(property2) == 1:
        return property1 in property2
    else:
        return False


def data_frame_properties_intersection(property1, property2):
    """
    Determine the intersection of two TimeSeriesDataFrame properties.

    If the intersection is empty, an empty list is returned.
    Since the properties can be scalars or vectors, this check is more
    than just a single boolean statement.

    :param property1: First property to check
    :param property2: Second property to check
    :return: List of column names in the intersection
    """
    p1_iterable = is_iterable_but_not_string(property1)
    p2_iterable = is_iterable_but_not_string(property2)

    if p1_iterable and p2_iterable:
        return list(set(property1).intersection(set(property2)))
    elif (not p1_iterable) and (not p2_iterable):
        return [property1] if property1 == property2 else []
    elif p1_iterable and (not p2_iterable):
        return list(set(property1).intersection(set([property2])))
    elif (not p1_iterable) and p2_iterable:
        return list(set(property2).intersection(set([property1])))
    else:
        return []


def check_cols_exist(df, cols):
    """
    Check whether cols exist in X.

    :param X: A TimeSeriesDataFrame or pandas.DataFrame_.

    :param cols: str or array-like, a column name or a list of column names.

    :return: None.
    """
    if is_iterable_but_not_string(cols):
        for col in cols:
            if col not in df.columns:
                error_message = ('Column {0} is not found '.format(col) +
                                 'in data frame')
                raise DataFrameMissingColumnException(error_message)
    elif isinstance(cols, str):
        if cols not in df.columns:
            error_message = 'Column {0} is not found in data frame'.format(
                cols)
            raise DataFrameMissingColumnException(error_message)
    else:
        error_message = 'Column name(s) must be a string or a list of strings.'
        raise TypeError(error_message)


def is_int_like(x):
    """
    Check if input is either native Python integer or a nump integer subtype.

    :param x: Input object
    :return: True if input is integer-like
    """
    return (isinstance(x, int) or issubclass(type(x), np.integer))


def is_large_enough(x, min_value):
    """Check if input is at least equal to `min_value`, complain if not."""
    if x < min_value:
        input_too_small_error = ("Input argument must be at least equal " +
                                 "to {}").format(min_value)
        input_too_small_details = ("instead got: {}").format(x)
        raise NotSupportedException(input_too_small_error,
                                    input_too_small_details)

###############################################################################


def is_datetime_like(x):
    """
    Check if argument is a legitimate datetime-like object.

    Only such objects can be put into time indices.

    :param x: Input Object
    :return: True if input is datetime-like
    """
    return any(isinstance(x, time_col_type)
               for time_col_type in ALLOWED_TIME_COLUMN_TYPES)

###############################################################################


def check_type_collection_or_dict(x, x_type_check_fun, x_expected_keys=None,
                                  x_valid_input_fun=None, **kwargs):
    """
    Check that input is a collection or dictionary.

    The input can be either a singleton of certain type, a collection of
    such types, or a dictionary with keys of the same type.

    :param x: input argument to be examined and verified for conformity
    :type x: singleton, collection, or dict

    :param x_type_check_fun:
        Function that checks type conformity of `x` when it's a singleton, or
        conformity of every element in `x` when it is a collection, or every
        element in `x.values()` when `x` is a dict. E.g. when checking forecast
        horizons, `x_type_check_fun` would ensure horizons are integers.
    :type x_type_check_fun: function

    :param x_expected_keys:
        When `x` is a dict, its keys are verified against this argument, and
        they have to match it exactly. Primary usage is to verify that all
        grains in a TimeSeriesDataFrame are addressed. Defaults to `None`
        to force an input when `x` is a dict, gets ignored otherwise.
    :type x_expected_keys: a collection that can be reduced to a set

    :param x_valid_input_fun:
        Optional function that verifies whether singleton `x` or its elements
        conform to downstream expectations. E.g. when checking forecast
        horizons this lets us ensure they are positive.
    :type x_valid_input_fun: function

    :param **kwargs:
        additional parameters to pass into the `x_valid_input_fun` function
    :type **kwargs: dict

    :rtype: `None` if all checks pass, otherwise exceptions are raised

    """
    if x_type_check_fun(x):
        if x_valid_input_fun is not None:
            x_valid_input_fun(x, **kwargs)
    elif is_iterable_but_not_string(x) and not isinstance(x, dict):
        [x_type_check_fun(y) for y in x]
        if x_valid_input_fun is not None:
            [x_valid_input_fun(y, **kwargs) for y in x]
    elif isinstance(x, dict):
        # check keys
        if x_expected_keys is None:
            x_expected_keys = set()
        rogue_keys = set(x.keys()).symmetric_difference(set(x_expected_keys))
        if len(rogue_keys) > 0:
            key_mismatch_error = ("When input is a dictionary, its keys must " +
                                  "be equal to `x_expected_keys`")
            key_mismatch_error_details = (
                "mismatched keys are: {}").format(rogue_keys)
            raise NotSupportedException(key_mismatch_error,
                                        key_mismatch_error_details)
        # check values
        for val in x.values():
            if x_type_check_fun(val):
                if x_valid_input_fun is not None:
                    x_valid_input_fun(val, **kwargs)
            elif is_iterable_but_not_string(val) and not isinstance(val, dict):
                [x_type_check_fun(y) for y in val]
                if x_valid_input_fun is not None:
                    [x_valid_input_fun(y, **kwargs) for y in val]
            else:
                wrong_val_type = ("When input is a dictionary, its keys must " +
                                  "be singletons or iterables of those")
                wrong_val_type_details = ("instead got {}".format(type(val)))
                raise NotSupportedException(wrong_val_type,
                                            wrong_val_type_details)
    else:
        wrong_input_type_error = ("Input argument can be a singleton, an " +
                                  "iterable, or a dictionary")
        wrong_input_type_details = ("instead got {}".format(type(x)))
        raise NotSupportedException(wrong_input_type_error,
                                    wrong_input_type_details)
###############################################################################


def is_collection(x):
    """Return `True` if `x` is a list, tuple, or set, `False` otherwise."""
    return is_iterable_but_not_string(x) and not isinstance(x, dict)
###############################################################################


def validate_and_sanitize_horizon(h, x_keys, include_all):
    """
    Check if input can be interpreted as forecast horizon and return it in a dictionary.

    :param: h
        Forecast horizon. Can be either a single integer, an iterable of
        integers, or a dict whose keys are TimeSeriesDataFrame grains and
        values are either ints or iterables of ints.
    :type h: int, iterable, or dict

    :param x_keys:
        When `h` is a dictionary, its keys must be exactly the same as `x_keys`,
        otherwise `NotSupportedException` is raised. If user wants separate
        forecast horizons per grain, then they must provide inputs for ALL
        grains.
    :type x_keys: iterable that can be reduced to set

    :param include_all:
        If `True`, all horizons from `min(h)` to `max(h)` will be returned, and
        if `h` is a single int, `min(h)` will be set to `1`. If `h` has more
        than two elements, a warning will be printed. E.g. if `h = [1, 2, 4]`
        and `include_all=True`, horizons `1` through `4` will be returned and a
        warning will be printed. If `False`, only the specified horizons are
        returned, e.g. `[1, 2, 4]` in the above example.
    :type include_all: bool

    :rtype: dict
    """
    # case 1: input is an int
    if is_int_like(h):
        is_large_enough(h, min_value=1)
        if include_all:
            horizons = list(np.arange(h) + 1)
            result = {key: horizons for key in x_keys}
        else:
            result = {key: [h] for key in x_keys}
    # case 2: input is an iterable of ints
    elif is_collection(h):
        if not all(is_int_like(x) for x in h):
            raise ValueError(("When `horizon` is an iterable, each element " +
                              "must be int-like!"))
        [is_large_enough(x, min_value=1) for x in h]
        if include_all:
            if len(h) > 2:
                too_many_inputs = ("When `horizon` is an iterable, and " +
                                   "`include_all` is `True`, all horizons " +
                                   "between min and max in the input will " +
                                   "be returned. Set `include_all` to " +
                                   "`False` if you only need a specific " +
                                   "subset of horizons!")
                warn(too_many_inputs, UserWarning)
            horizons = list(np.arange(min(h), max(h) + 1))
            result = {key: horizons for key in x_keys}
        else:
            result = {key: list(h) for key in x_keys}
    # case 3: input is a dict
    elif isinstance(h, dict):
        if x_keys is None:
            x_keys = set()
        rogue_keys = set(h.keys()).symmetric_difference(set(x_keys))
        if len(rogue_keys) > 0:
            key_mismatch_error = (
                "When `horizon` is a dictionary, its keys must " +
                "be equal to grains of TimeSeriesDataFrame `X`")
            key_mismatch_error_details = (
                "mismatched keys are: {}").format(rogue_keys)
            raise NotSupportedException(key_mismatch_error,
                                        key_mismatch_error_details)
        result = dict()
        for k, v in h.items():
            # case 3.1: value is an int
            if is_int_like(v):
                is_large_enough(v, min_value=1)
                if include_all:
                    horizons = list(np.arange(v) + 1)
                    result[k] = horizons
                else:
                    result[k] = [v]
            # case 3.2: value is an iterable of its
            elif is_collection(v):
                if not all(is_int_like(x) for x in v):
                    raise ValueError(("When `horizon` is a dict whose keys " +
                                      "are iterables, all its elements " +
                                      "must be int-like!"))
                [is_large_enough(x, min_value=1) for x in v]
                if include_all:
                    if len(v) > 2:
                        too_many_inputs = (
                            "When `horizon` is a dict and its values are " +
                            "iterables, and `include_all` is `True`, all " +
                            "horizons between min and max in the input will " +
                            "be returned. Set `include_all` to `False` if " +
                            "you only need a specific subset of horizons!")
                        warn(too_many_inputs, UserWarning)
                    horizons = list(np.arange(min(v), max(v) + 1))
                    result[k] = horizons
                else:
                    result[k] = list(v)
            # case 3.3: anything else is not supported
            else:
                wrong_values_err = ("When `horizon` is a dict, its values can " +
                                    "either be int-like or iterables of " +
                                    "int-likes")
                wrong_values_detail = ("instead for grain {0} got {1}").format(
                    k, type(v))
                raise NotSupportedException(wrong_values_err,
                                            wrong_values_detail)
    # case 4: anything else is not supported
    else:
        wrong_input_err = ("Input `horizon` can be int-like, an iterable " +
                           "of int-likes, or a dict")
        wrong_input_detail = ("instead got {0}").format(type(h))
        raise NotSupportedException(wrong_input_err, wrong_input_detail)
    return result
################################################################################


def validate_and_sanitize_end_dates(d, X, include_all):
    """
    Check if input argument is a forecast date(s), and return it as a dictionary.

    :param: d
        Dates for which forecasts are sought. Can be either a single datetime,
        an iterable of datetimes, or a dict whose keys are TimeSeriesDataFrame
        grains and values are either datetimes or iterables of datetimes.
    :type h: int, iterable, or dict

    :param X:
        TimeSeriesDataFrame on which models are trained. Used to validate that
        all the grains are provided if `d` is a dict, and to store latest
        actual date per grain to warn of potential overlaps.
    :type X: TimeSeriesDataFrame

    :param include_all:
        If `True`, all dates from `min(d)` to `max(d)` will be returned, and
        if `d` is a single date, `min(d)` will be set to next date after
        the last actual date in X per grain. If `d` has more
        than two elements, a warning will be printed. If `False`, only the
        specified dates are returned.
    :type include_all: bool

    :rtype: dict
    """
    # Private helper method to catch date overlap
    def warn_if_dates_overlap(existing_dates, new_dates):
        from .forecasting_utils import flatten_list
        latest = pd.to_datetime(max(flatten_list([existing_dates])))
        earliest = pd.to_datetime(min(flatten_list([new_dates])))
        if earliest <= latest:
            warn(("Some of the dates provided in `end_time` will overlap with " +
                  "the dates in the input TimeSeriesDataFrame `X`!"),
                 UserWarning)
    # ## Another private method to get min of maybe-iterable-like object

    def reduce_date(x, fun=min):
        if is_datetime_like(x) and not is_collection(x):
            ans = x
        elif is_collection(x):
            ans = fun(x)
        elif isinstance(x, dict):
            ans = fun(fun(y) if is_collection(y) else y for y in x.values())
        else:
            raise ValueError('Invalid input argument type!')
        return(ans)
    # main code
    X_freq = X.infer_freq()
    x_dates = X.groupby_grain().apply(lambda x: x.time_index.max()).to_dict()
    # by default, pandas.to_datetime() returns a DatetimeIndex object, which
    # even of length 1, is an array, so is iterable. We have to change the
    # validation logic to accommodate for this.

    # another piece that needs handling - what if X has origin_time set
    if X.origin_time_colname is not None:
        if max(X.time_index) > reduce_date(d):
            error_message = ("When input TimeSeriesDataFrame has " +
                             "`origin_time` set, `future_date` must come " +
                             "after `time_index`s.")
            raise NotSupportedException(error_message)

    # case 1: singleton non-iterable
    if is_datetime_like(d) and not is_collection(d):
        warn_if_dates_overlap(max(x for x in x_dates.values()), d)
        if include_all:
            result = dict()
            for grain, last_date in x_dates.items():
                date_range = sorted(pd.date_range(start=last_date,
                                                  end=d, freq=X_freq))
                if len(date_range) > 1:
                    date_range = date_range[1:]
                result[grain] = sorted(date_range)
        else:
            result = {grain: [pd.to_datetime(d)] for grain in x_dates.keys()}
    # case 2: iterable of datetimes
    elif is_collection(d):
        # now work with d_iter as a list of datetime_like objects
        if not all(is_datetime_like(x) for x in d):
            raise ValueError(("When `end_time` is an iterable, each of its " +
                              "elements must be datetime-like"))
        # the following line turns pd.to_datetime([x, y]) into [x, y] of
        # type timestamp
        d_iter = sorted(d)
        [warn_if_dates_overlap(max(x for x in x_dates.values()), y)
         for y in d_iter]
        if include_all:
            if len(d_iter) > 2:
                too_many_inputs = ("When `end_date` is an iterable, and " +
                                   "`include_all` is `True`, all dates " +
                                   "between min and max in the input will be " +
                                   "returned. Set `include_all` to `False` " +
                                   "if you only need a specific subset " +
                                   "of dates!")
                warn(too_many_inputs, UserWarning)
            date_range = sorted(pd.date_range(start=min(d_iter),
                                              end=max(d_iter), freq=X_freq))
        else:
            date_range = sorted(list({pd.to_datetime(x) for x in d_iter}))
        result = {key: date_range for key in x_dates.keys()}
        # result = {key: d_iter for key in x_dates.keys()}
    # case 3: input is a dict
    elif isinstance(d, dict):
        rogue_keys = set(d.keys()).symmetric_difference(set(x_dates.keys()))
        if len(rogue_keys) > 0:
            key_mismatch_error = (
                "When `end_date` is a dictionary, its keys must " +
                "be equal to grains of TimeSeriesDataFrame `X`")
            key_mismatch_error_details = (
                "mismatched keys are: {}").format(rogue_keys)
            raise NotSupportedException(key_mismatch_error,
                                        key_mismatch_error_details)
        result = dict()
        for k, v in d.items():
            # case 3.1: value is an datetime-like singleton
            if is_datetime_like(v) and not is_collection(v):
                warn_if_dates_overlap(x_dates[k], v)
                if include_all:
                    result[k] = sorted(pd.date_range(start=x_dates[k], end=v,
                                                     freq=X_freq))
                else:
                    result[k] = [pd.to_datetime(v)]
            # case 3.2: value is an iterable of datetime_likes
            elif is_collection(v):
                if not all(is_datetime_like(x) for x in v):
                    raise ValueError(("When `end_time` is a dict whose keys " +
                                      "are iterables, each of its elements " +
                                      "must be datetime-like"))
                v_iter = sorted(v)
                [warn_if_dates_overlap(x_dates[k], y) for y in v_iter]
                if include_all:
                    if len(v_iter) > 2:
                        too_many_inputs = (
                            "When `end_date` is a dict and its values are " +
                            "iterables, and `include_all` is `True`, all " +
                            "dates between min and max in the input will " +
                            "be returned. Set `include_all` to `False` if " +
                            "you only need a specific subset of dates!")
                        warn(too_many_inputs, UserWarning)
                    date_range = sorted(pd.date_range(start=min(v_iter),
                                                      end=max(v_iter),
                                                      freq=X_freq))
                else:
                    date_range = sorted(list(
                        {pd.to_datetime(x) for x in v_iter}))
                result[k] = date_range
            # case 3.3: anything else is not supported
            else:
                wrong_values_err = ("When `end_date` is a dict, its values can " +
                                    "either be datetime-like or iterables " +
                                    "of such")
                wrong_values_detail = ("instead for grain {0} got {1}").format(
                    k, type(v))
                raise NotSupportedException(wrong_values_err,
                                            wrong_values_detail)
    # case 4: anything else is not supported
    else:
        wrong_input_err = ("Input `end_date` can be datetime-like, an iterable " +
                           "of datetime-likes, or a dict")
        wrong_input_detail = ("instead got {0}").format(type(d))
        raise NotSupportedException(wrong_input_err, wrong_input_detail)
    return result
################################################################################
