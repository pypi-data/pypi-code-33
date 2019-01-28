# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for validation and conversion."""
import collections
import json
import os
import sys
import traceback
import warnings
from math import sqrt

import numpy as np
import pandas as pd
import pandas.api as api
import pkg_resources
import scipy
from sklearn import model_selection

from automl.client.core.common import constants, datasets, pipeline_spec
from automl.client.core.common.constants import Metric, NumericalDtype
from automl.client.core.common.exceptions import (DataException,
                                                  ServiceException)
from automl.client.core.common.metrics import minimize_or_maximize

SOURCE_WRAPPER_MODULE = 'automl.client.core.common.model_wrappers'
MAPPED_WRAPPER_MODULE = 'azureml.train.automl.model_wrappers'


def get_value_int(intstring):
    """
    Convert string value to int.

    :param intstring: The input value to be converted.
    :type intstring: str
    :return: The converted value.
    :rtype: int
    """
    if intstring is not None and intstring is not '':
        return int(intstring)
    return intstring


def get_value_float(floatstring):
    """
    Convert string value to float.

    :param intstring: The input value to be converted.
    :type intstring: str
    :return: The converted value.
    :rtype: float
    """
    if floatstring is not None and floatstring is not '':
        return float(floatstring)
    return floatstring


def get_value_from_dict(dictionary, names, default_value):
    """
    Get the value of a configuration item that has a list of names.

    :param dictionary:
        Dictory of settings with key value pair to look the data for.
    :param names: The list of names for the item looking foi.
    :param default_value: Default value to return if no matching key found
    :return: Returns the first value from the list of names.
    """
    for key in names:
        if key in dictionary:
            return dictionary[key]
    return default_value


def extract_user_data(user_script):
    """
    Extract data from user's module containing get_data().

    This method automatically runs during an automated machine learning experiment.

    :param user_script: Python module containing get_data() function.
    :return: Dictionary containing
        X_train, y_train, sample_weight, X_valid, y_valid,
        sample_weight_valid, cv_splits_indices.
    """
    if user_script is None:
        raise ValueError(
            "Get data script was not defined and X,"
            " y inputs were not provided.")
    try:
        output = user_script.get_data()
    except Exception:
        raise DataException(
            "Could not execute get_data() from user script.") from None
    if isinstance(output, dict):
        return _extract_data_from_dict(output)
    elif isinstance(output, tuple):
        return _extract_data_from_tuple(output)
    else:
        raise DataException("Could not extract data from user script.")


def _y_nan_check(output=None):
    y = output['y']
    X = output['X']
    sample_weight = output['sample_weight']
    if y is not None and pd.isnull(y).any():
        warnings.warn(
            "Labels contain NaN values. Removing for AutoML Experiment.")
        y_indices_pruned = ~pd.isnull(y)
        X_reduced = X[y_indices_pruned]
        y_reduced = y[y_indices_pruned]
        sample_weight_reduced = None
        if sample_weight is not None:
            sample_weight_reduced = sample_weight[y_indices_pruned]
        if y_reduced.shape[0] is 0:
            raise DataException('All label data is NaN.')
        output['X'] = X_reduced
        output['y'] = y_reduced
        output['sample_weight'] = sample_weight_reduced
    y_valid = output['y_valid']
    X_valid = output['X_valid']
    sample_weight_valid = output['sample_weight_valid']
    if y_valid is not None and pd.isnull(y_valid).any():
        warnings.warn(
            "Validation Labels contain NaN values. "
            "Removing for AutoML Experiment.")
        y_valid_indices_pruned = ~pd.isnull(y_valid)
        X_valid_reduced = X_valid[y_valid_indices_pruned]
        y_valid_reduced = y_valid[y_valid_indices_pruned]
        sample_weight_valid_reduced = None
        if sample_weight_valid is not None:
            sample_weight_valid_reduced = \
                sample_weight_valid[y_valid_indices_pruned]
        output['X_valid'] = X_valid_reduced
        output['y_valid'] = y_valid_reduced
        output['sample_weight_valid'] = sample_weight_valid_reduced
    return output


def _extract_data_from_tuple(output):
    """
    Extract user data if it is passed as a tuple.

    :param output: tuple containing user data
    :return: tuple containing X_train, y_train, X_test, y_test
    """
    X_valid, y_valid = None, None
    if len(output) < 2:
        raise DataException("Could not extract X, y from get_data() in user "
                            "script. get_data only output {0} values."
                            .format(len(output))) from None
    x_raw_column_names = None
    X = output[0]
    y = output[1]
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
        X = X.values
    if isinstance(y, pd.DataFrame):
        y = y.values

    if len(output) >= 4:
        X_valid = output[2]
        y_valid = output[3]
        if isinstance(y_valid, pd.DataFrame):
            y_valid = y_valid.values
        if isinstance(X_valid, pd.DataFrame):
            X_valid = X_valid.values

    return {
        "X": X,
        "y": y,
        "sample_weight": None,
        "x_raw_column_names": x_raw_column_names,
        "X_valid": X_valid,
        "y_valid": y_valid,
        "sample_weight_valid": None,
        "X_test": None,
        "y_test": None,
        "cv_splits_indices": None,
    }


def _extract_data_from_dict(output):
    """
    Extract user data if it is passed as a dictionary.

    :param output: dictionary containing user data and metadata
    :return: Dictionary containing AutoML relevant data
    """
    X = get_value_from_dict(output, ['X'], None)
    y = get_value_from_dict(output, ['y'], None)
    sample_weight = get_value_from_dict(output, ['sample_weight'], None)
    X_valid = get_value_from_dict(output, ['X_valid'], None)
    y_valid = get_value_from_dict(output, ['y_valid'], None)
    sample_weight_valid = get_value_from_dict(
        output, ['sample_weight_valid'], None)
    X_test = get_value_from_dict(output, ['X_test'], None)
    y_test = get_value_from_dict(output, ['y_test'], None)
    data = get_value_from_dict(output, ['data_train'], None)
    columns = get_value_from_dict(output, ['columns'], None)
    label = get_value_from_dict(output, ['label'], None)
    cv_splits_indices = get_value_from_dict(
        dictionary=output,
        names=["cv_splits_indices"], default_value=None)
    x_raw_column_names = None

    if data is not None:
        if label is None and X is None and y is None:
            raise DataException('Pandas data array received without a label. '
                                'Please add a ''label'' element to the '
                                'get_data() output.')
        if not isinstance(label, list):
            assert(isinstance(label, str) or isinstance(label, int))
            label = [label]
        y_extracted = data[label].values
        X_extracted = data[data.columns.difference(label)]
        if columns is not None:
            X_extracted = X_extracted[X_extracted.columns.intersection(
                columns)]

        if X is None and y is None:
            X = X_extracted
            y = y_extracted
        else:
            if np.array_equiv(X, X_extracted.values):
                raise DataException(
                    "Different values for X and data were provided. "
                    "Please return either X and y or data and label.")
            if np.array_equiv(y, y_extracted.values):
                raise DataException(
                    "Different values for y and label were provided. "
                    "Please return either X and y or data and label.")
    if isinstance(X, pd.DataFrame):
        x_raw_column_names = X.columns.values
        X = X.values
    if isinstance(X_valid, pd.DataFrame):
        X_valid = X_valid.values
    if isinstance(X_test, pd.DataFrame):
        X_test = X_test.values
    if isinstance(y, pd.DataFrame):
        y = y.values
    if isinstance(y_valid, pd.DataFrame):
        y_valid = y_valid.values
    if isinstance(y_test, pd.DataFrame):
        y_test = y_test.values

    if X is None:
        raise DataException(
            "Could not retrieve X train data from get_data() call. "
            "Please ensure you are either returning either "
            "{X_train: <numpy array>, y_train: <numpy array>"
            "or {data: <pandas dataframe>, label: <string>")
    if y is None:
        raise DataException(
            "Could not retrieve y train data from get_data() call. "
            "Please ensure you are either returning either "
            "{X_train: <numpy array>, y_train: <numpy array>"
            "or {data: <pandas dataframe>, label: <string>")

    if (X_valid is None) is not (y_valid is None):
        raise DataException(
            'Received only one of X_valid or y_valid.'
            'Either both or neither value should be provided.')

    return {
        "X": X,
        "y": y,
        "x_raw_column_names": x_raw_column_names,
        "sample_weight": sample_weight,
        "X_valid": X_valid,
        "y_valid": y_valid,
        "sample_weight_valid": sample_weight_valid,
        "X_test": X_test,
        "y_test": y_test,
        "cv_splits_indices": cv_splits_indices,
    }


def _log_traceback(exception, logger):
    logger.error(exception)
    logger.error(traceback.format_exc())


def _make_printable(pipeline_obj):
    pipeline_pretty = ''
    if pipeline_obj is not None:
        if isinstance(pipeline_obj, str):
            pipeline_pretty = pipeline_obj
        else:
            for step in pipeline_obj.steps:
                pipeline_pretty += ' ' + str(step[0])
    return pipeline_pretty


def _read_compute_file(run_configuration, path):
    compute_dict = {}
    try:
        with open(os.path.join(
                path, "aml_config",
                "{}.compute".format(run_configuration))) as compute_file:
            for line in compute_file:
                key, value = line.strip().split(': ')
                compute_dict[key] = value
    except Exception as e:
        # In the event that a compute has multiple defined run configs,
        # i.e. docker.compute starts with docker-python.runconfig
        # and docker-spark.runconfig
        # TODO: need less brittle logic for this
        run_compute = run_configuration.split('-')[0]
        with open(os.path.join(
                path, "aml_config",
                "{}.compute".format(run_compute))) as compute_file:
            for line in compute_file:
                if line.startswith('#'):
                    continue
                key, value = line.strip().split(': ')
                compute_dict[key] = value
    return compute_dict


def _get_column_data_type_as_str(array):
    """
    Get the type of ndarray by looking into the ndarray contents.

    :param array: ndarray
    :raise ValueError if array is not ndarray or not valid
    :return: type of column as a string (integer, floating, string etc.)
    """
    # If the array is not valid, then throw exception
    if array is None:
        raise DataException("The input array is None")

    # If the array is not an instance of ndarray, then throw exception
    if not isinstance(array, np.ndarray):
        raise DataException("Not an instance of ndarray")

    # Ignore the Nans and then return the data type of the column
    return api.types.infer_dtype(array[~pd.isnull(array)])


def _check_if_column_data_type_is_numerical(data_type_as_string):
    """
    Check if column data type is numerical.

    :param data_type_as_string: string carrying the type from infer_dtype()
    :return: boolean 'True' if the dtype returned is 'integer', 'floating', 'mixed-integer' or 'mixed-integer-float'.
                     'False' otherwise.
    """
    if data_type_as_string in list(NumericalDtype.FULL_SET):
        return True

    return False


def _check_if_column_data_type_is_int(data_type_as_string):
    """
    Check if column data type is integer.

    :return: boolean 'True' if the dtype returned is 'integer'. 'False' otherwise.
    """
    if data_type_as_string == NumericalDtype.Integer:
        return True

    return False


def _all_dependencies():
    """
    Retrieve the packages from the site-packages folder by using pkg_resources.

    :return: A dict contains packages and their corresponding versions.
    """
    dependencies_versions = dict()
    for d in pkg_resources.working_set:
        dependencies_versions[d.key] = d.version
    return dependencies_versions


def _is_sdk_package(name):
    """Check if a package is in sdk by checking the whether the package startswith('azureml')."""
    return name.startswith('azureml')


def get_sdk_dependencies(
    all_dependencies_versions=None,
    logger=None,
    **kwargs
):
    """
    Return the package-version dict.

    :param all_dependencies_versions:
        If None, then get all and filter only the sdk ones.
        Else, only check within the that dict the sdk ones.
    :param logger: The logger.
    :return: The package-version dict.
    """
    sdk_dependencies_version = dict()
    if all_dependencies_versions is None:
        all_dependencies_versions = _all_dependencies()
    for d in all_dependencies_versions:
        if _is_sdk_package(d):
            sdk_dependencies_version[d] = all_dependencies_versions[d]

    return sdk_dependencies_version


def _check_dependencies_versions(old_versions, new_versions):
    """
    Check the SDK packages between the training environment and the predict environment.

    Then it gives out 2 kinds of warning combining sdk/not sdk with missing or version mismatch.

    :param old_versions: Packages in the training environment.
    :param new_versions: Packages in the predict environment.
    :return: sdk_dependencies_mismatch, sdk_dependencies_missing,
             other_depencies_mismatch, other_depencies_missing
    """
    sdk_dependencies_mismatch = set()
    other_depencies_mismatch = set()
    sdk_dependencies_missing = set()
    other_depencies_missing = set()

    for d in old_versions.keys():
        if d in new_versions and old_versions[d] != new_versions[d]:
            if _is_sdk_package(d):
                sdk_dependencies_mismatch.add(d)
            else:
                other_depencies_mismatch.add(d)
        elif d not in new_versions:
            if _is_sdk_package(d):
                sdk_dependencies_missing.add(d)
            else:
                other_depencies_missing.add(d)

    return sdk_dependencies_mismatch, sdk_dependencies_missing, \
        other_depencies_mismatch, other_depencies_missing


def _check_dimensions(
        X, y, X_valid, y_valid, sample_weight, sample_weight_valid):
    dimension_error_message = "Dimension mismatch for {0} data. " \
                              "Expecting {1} dimensional array, " \
                              "but received {2} dimensional data."
    feature_dimensions = 2
    label_dimensions = 1
    if isinstance(X, pd.DataFrame):
        if X.values.ndim > feature_dimensions:
            raise ValueError(
                dimension_error_message
                .format("X", feature_dimensions, X.values.ndim))
    if isinstance(y, pd.DataFrame):
        if y.shape[1] != label_dimensions:
            raise ValueError(
                dimension_error_message
                .format("y", label_dimensions, X.values.ndim))
    if isinstance(X_valid, pd.DataFrame):
        if X_valid.values.ndim > feature_dimensions:
            raise ValueError(
                dimension_error_message
                .format("X_valid", feature_dimensions, X.values.ndim))
    if isinstance(y_valid, pd.DataFrame):
        if y_valid.shape[1] != label_dimensions:
            raise ValueError(
                dimension_error_message
                .format("y_valid", label_dimensions, X.values.ndim))
    if isinstance(sample_weight, pd.DataFrame):
        if sample_weight.shape[1] != label_dimensions:
            raise ValueError(
                dimension_error_message
                .format("sample_weight", label_dimensions, X.values.ndim))
    if isinstance(sample_weight_valid, pd.DataFrame):
        if sample_weight_valid.shape[1] != label_dimensions:
            raise ValueError(
                dimension_error_message.format(
                    "sample_weight_valid", label_dimensions, X.values.ndim))

    if isinstance(X, np.ndarray):
        if X.ndim > feature_dimensions:
            raise ValueError(
                dimension_error_message
                .format("X", feature_dimensions, X.ndim))
    if isinstance(y, np.ndarray):
        if y.ndim != label_dimensions:
            raise ValueError(
                dimension_error_message
                .format("y", label_dimensions, X.ndim))
    if isinstance(X_valid, np.ndarray):
        if X_valid.ndim > feature_dimensions:
            raise ValueError(
                dimension_error_message
                .format("X_valid", feature_dimensions, X.ndim))
    if isinstance(y_valid, np.ndarray):
        if y_valid.ndim != label_dimensions:
            raise ValueError(
                dimension_error_message
                .format("y_valid", label_dimensions, X.ndim))
    if isinstance(sample_weight, np.ndarray):
        if sample_weight.ndim != label_dimensions:
            raise ValueError(
                dimension_error_message
                .format("sample_weight", label_dimensions, X.ndim))
    if isinstance(sample_weight_valid, np.ndarray):
        if sample_weight_valid.ndim != label_dimensions:
            raise ValueError(
                dimension_error_message
                .format("sample_weight_valid", label_dimensions, X.ndim))

    if X is not None and y is not None and X.shape[0] != y.shape[0]:
        raise ValueError(
            "X and y data do not have the same number of samples. "
            "X has {0} samples and y has {1} samples."
            .format(X.shape[0], y.shape[0]))
    if X_valid is not None and y_valid is not None and \
            X_valid.shape[0] != y_valid.shape[0]:
        raise ValueError(
            "X_valid and y_valid data do not have the same number "
            "of samples. X_valid has {0} samples and "
            "y_valid has {1} samples."
            .format(X_valid.shape[0], y_valid.shape[0]))
    if sample_weight is not None and y is not None and \
            sample_weight.shape[0] != y.shape[0]:
        raise ValueError(
            "sample_weight and y data do not have the same number "
            "of samples. sample_weight has {0} samples and "
            "y has {1} samples."
            .format(sample_weight.shape[0], y.shape[0]))
    if sample_weight_valid is not None and y_valid is not None and\
            sample_weight_valid.shape[0] != y_valid.shape[0]:
        raise ValueError(
            "sample_weight_valid and y_valid data do not have the same number "
            "of samples. sample_weight_valid has {0} samples and y_valid "
            "has {1} samples.".format(sample_weight.shape[0], y.shape[0]))


def _get_max_min_comparator(objective):
    """Return a comparator either maximizing or minimizing two values. Will not handle nans."""
    if objective == constants.OptimizerObjectives.MAXIMIZE:
        def maximize(x, y):
            if x >= y:
                return x
            else:
                return y
        return maximize
    elif objective == constants.OptimizerObjectives.MINIMIZE:
        def minimize(x, y):
            if x <= y:
                return x
            else:
                return y
        return minimize
    else:
        raise ValueError(
            "Maximization or Minimization could not be determined "
            "based on current metric.")


def sparse_std(x):
    """
    Compute the std for a sparse matrix.

    Std is computed by dividing by N and not N-1 to match numpy's computation.

    :param x: sparse matrix
    :return: std dev
    """
    if not scipy.sparse.issparse(x):
        raise ValueError("x is not a sparse matrix")

    mean_val = x.mean()
    num_els = x.shape[0] * x.shape[1]
    nzeros = x.nonzero()
    sum = mean_val**2 * (num_els - nzeros[0].shape[0])
    for i, j in zip(*nzeros):
        sum += (x[i, j] - mean_val)**2

    return sqrt(sum / num_els)


def sparse_isnan(x):
    """
    Return whether any element in matrix is nan.

    :param x: sparse matrix
    :return: True/False
    """
    if not scipy.sparse.issparse(x):
        raise ValueError("x is not sparse matrix")

    for i, j in zip(*x.nonzero()):
        if np.isnan(x[i, j]):
            return True

    return False


def subsampling_recommended(num_samples, num_iterations=None):
    """
    Return whether or not subsampling is recommended for the current scenario.

    :param x: sparse matrix
    :return: True/False
    """
    return num_samples >= 50000 and \
        ((not num_iterations) or
         num_iterations >= 85)


def stratified_shuffle(indices, y, random_state):
    """
    Shuffle an index in a way such that the first 1%, 2%, 4% etc. are all stratified samples.

    The way we achieve this is, first get 1:99 split
    then for the 99 part, we do a split of 1:98
    and then in the 98 part, we do a split of 2:96
    and then in the 96 part, we split 4:92
    then 8:86
    then 16:70
    then 32:38
    """
    splits = [
        [1, 99],
        [1, 98],
        [2, 96],
        [4, 92],
        [8, 86],
        [16, 70],
        [32, 38]]

    ret = []
    y_left = y

    for split in splits:
        kept_frac = float(split[0]) / (split[0] + split[1])
        kept, left = model_selection.train_test_split(
            indices,
            train_size=kept_frac,
            stratify=y_left,
            random_state=random_state)
        ret = np.concatenate([ret, kept])
        indices = left
        y_left = y[left]

    ret = np.concatenate([ret, left]).astype('int')
    return ret


def _log_raw_data_stat(raw_feature_stats, logger=None, prefix_message=None):
    if logger is None:
        return
    if prefix_message is None:
        prefix_message = ""
    raw_feature_stats_dict = dict()
    for name, stats in raw_feature_stats.__dict__.items():
        try:
            stats_json_str = json.dumps(stats)
        except (ValueError, TypeError):
            stats_json_str = json.dumps(dict())
        raw_feature_stats_dict[name] = stats_json_str
    logger.info(
        "{}RawFeatureStats:{}".format(
            prefix_message, json.dumps(raw_feature_stats_dict)
        )
    )


def _get_ts_params_dict(automl_settings):
    if automl_settings.is_timeseries:
        return {
            constants.TimeSeries.TIME_COLUMN_NAME: automl_settings.time_column_name,
            constants.TimeSeries.GRAIN_COLUMN_NAMES: automl_settings.grain_column_names,
            constants.TimeSeries.DROP_COLUMN_NAMES: automl_settings.drop_column_names
        }
    else:
        return None
