# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""automated machine learning SDK utilities."""
import json

import numpy as np
import pandas as pd
import scipy

from automl.client.core.common.utilities import (
    _check_if_column_data_type_is_numerical,
    _get_column_data_type_as_str,
    _check_dimensions,
    _y_nan_check,
    extract_user_data,
    get_sdk_dependencies
)

from automl.client.core.common.exceptions import ServiceException
from automl.client.core.common._engineered_feature_names import FeatureTypeRecognizer
from . import (_constants_azureml,
               _dataprep_utilities,
               constants)
from .constants import Metric


def _check_sample_weight(x, sample_weight, x_name,
                         sample_weight_name, automl_settings):
    """
    Validate sample_weight.

    :param x:
    :param sample_weight:
    :raise ValueError if sample_weight has problems
    :return:
    """
    if not isinstance(sample_weight, np.ndarray):
        raise ValueError(sample_weight_name + " should be numpy array")

    if x.shape[0] != len(sample_weight):
        raise ValueError(sample_weight_name +
                         " length should match length of " + x_name)

    if len(sample_weight.shape) > 1:
        raise ValueError(sample_weight_name +
                         " should be a unidimensional vector")

    if automl_settings.primary_metric in \
            Metric.SAMPLE_WEIGHTS_UNSUPPORTED_SET:
        raise ValueError("Sample weights is not supported for these"
                         " primary metrics: {0}".format(
                             Metric.SAMPLE_WEIGHTS_UNSUPPORTED_SET))


def _check_x_y(x, y, automl_settings):
    """
    Validate input data.

    :param x: input data. dataframe/ array/ sparse matrix
    :param y: input labels. dataframe/series/array
    :param automl_settings: automl settings
    :raise: ValueError if data does not conform to accepted types and shapes
    :return:
    """
    preprocess = automl_settings.preprocess
    is_timeseries = automl_settings.is_timeseries

    if x is None:
        raise ValueError("X should not be None")

    if y is None:
        raise ValueError("y should not be None")

    # If text data is not being preprocessed or featurized, then raise an error
    if not (preprocess is True or preprocess == "True") and not is_timeseries:
        without_preprocess_error_str = \
            "The training data contains {}, {} or {} data. Please set preprocess flag as True".format(
                FeatureTypeRecognizer.DateTime.lower(),
                FeatureTypeRecognizer.Categorical.lower(),
                FeatureTypeRecognizer.Text.lower())

        if isinstance(x, pd.DataFrame):
            for column in x.columns:
                if not _check_if_column_data_type_is_numerical(_get_column_data_type_as_str(x[column].values)):
                    raise ValueError(without_preprocess_error_str)
        elif isinstance(x, np.ndarray):
            if len(x.shape) == 1:
                if not _check_if_column_data_type_is_numerical(
                        _get_column_data_type_as_str(x)):
                    raise ValueError(without_preprocess_error_str)
            else:
                for index in range(x.shape[1]):
                    if not _check_if_column_data_type_is_numerical(
                            _get_column_data_type_as_str(x[:, index])):
                        raise ValueError(without_preprocess_error_str)

    if not (((preprocess is True or preprocess == "True") and
             isinstance(x, pd.DataFrame)) or
            isinstance(x, np.ndarray) or scipy.sparse.issparse(x)):
        raise ValueError(
            "x should be dataframe with preprocess set or numpy array"
            " or sparse matrix")

    if not isinstance(y, np.ndarray):
        raise ValueError("y should be numpy array")

    if x.shape[0] != y.shape[0]:
        raise ValueError("number of rows in x and y are not equal")

    if len(y.shape) > 2 or (len(y.shape) == 2 and y.shape[1] != 1):
        raise ValueError("y should be a vector Nx1")

    if automl_settings.task_type == constants.Tasks.REGRESSION:
        if not _check_if_column_data_type_is_numerical(
                _get_column_data_type_as_str(y)):
            raise ValueError(
                "Please make sure y is numerical before fitting for "
                "regression")


def _format_training_data(
        X=None, y=None, sample_weight=None, X_valid=None, y_valid=None, sample_weight_valid=None,
        data=None, label=None, columns=None, cv_splits_indices=None, user_script=None):
    """
    Create a dictionary with training and validation data from all supported input formats.

    :param X: Training features.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param sample_weight: Sample weights for training data.
    :type sample_weight: pandas.DataFrame pr numpy.ndarray or azureml.dataprep.Dataflow
    :param X_valid: validation features.
    :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y_valid: validation labels.
    :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param sample_weight_valid: validation set sample weights.
    :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param data: Training features and label.
    :type data: pandas.DataFrame
    :param label: Label column in data.
    :type label: str
    :param columns: whitelist of columns in data to use as features.
    :type columns: list(str)
    :param cv_splits_indices:
        Indices where to split training data for cross validation.
        Each row is a separate cross fold and within each crossfold, provide 2 arrays,
        the first with the indices for samples to use for training data and the second
        with the indices to use for validation data. i.e [[t1, v1], [t2, v2], ...]
        where t1 is the training indices for the first cross fold and v1 is the validation
        indices for the first cross fold.
    :type cv_splits_indices: numpy.ndarray
    :param user_script: File path to script containing get_data()
    :return:
    """
    data_dict = None
    x_raw_column_names = None

    if X is None and y is None and data is None:
        if data_dict is None:
            data_dict = extract_user_data(user_script)
        X = data_dict.get('X')
        y = data_dict.get('y')
        sample_weight = data_dict.get('sample_weight')
        X_valid = data_dict.get('X_valid')
        y_valid = data_dict.get('y_valid')
        sample_weight_valid = data_dict.get('sample_weight_valid')
        cv_splits_indices = data_dict.get("cv_splits_indices")
        x_raw_column_names = data_dict.get("x_raw_column_names")
    elif data is not None and label is not None:
        # got pandas DF
        X = data[data.columns.difference([label])]
        if columns is not None:
            X = X[X.columns.intersection(columns)]
        y = data[label].values

        # Get the raw column names
        if isinstance(X, pd.DataFrame):
            # Cache the raw column names if available
            x_raw_column_names = X.columns.values
    else:
        # Get the raw column names
        if isinstance(X, pd.DataFrame):
            # Cache the raw column names if available
            x_raw_column_names = X.columns.values
        else:
            X = _dataprep_utilities.try_retrieve_pandas_dataframe(X)
            y = _dataprep_utilities.try_retrieve_numpy_array(y)
            sample_weight = _dataprep_utilities.try_retrieve_numpy_array(
                sample_weight)
            X_valid = _dataprep_utilities.try_retrieve_pandas_dataframe(
                X_valid)
            y_valid = _dataprep_utilities.try_retrieve_numpy_array(y_valid)
            sample_weight_valid = _dataprep_utilities.try_retrieve_numpy_array(
                sample_weight_valid)
            cv_splits_indices = _dataprep_utilities.try_resolve_cv_splits_indices(
                cv_splits_indices)

    if isinstance(X, pd.DataFrame):
        X = X.values
    if isinstance(y, pd.DataFrame):
        y = y.values
    if isinstance(X_valid, pd.DataFrame):
        X_valid = X_valid.values
    if isinstance(y_valid, pd.DataFrame):
        y_valid = y_valid.values
    if isinstance(sample_weight, pd.DataFrame):
        sample_weight = sample_weight.values
    if isinstance(sample_weight_valid, pd.DataFrame):
        sample_weight_valid = sample_weight_valid.values

    data_dict = {
        'X': X,
        'y': y,
        'X_valid': X_valid,
        'y_valid': y_valid,
        'cv_splits_indices': cv_splits_indices,
        'x_raw_column_names': x_raw_column_names,
        'sample_weight': sample_weight,
        'sample_weight_valid': sample_weight_valid}
    return data_dict


def _validate_training_data(
        X, y, X_valid, y_valid, sample_weight, sample_weight_valid,
        cv_splits_indices, automl_settings):
    _check_x_y(X, y, automl_settings)

    # Ensure at least one form of validation is specified
    if not ((X_valid is not None) or automl_settings.n_cross_validations or
       (cv_splits_indices is not None) or automl_settings.validation_size):
        raise ValueError(
            "No form of validation was provided. Please specify the data "
            "or type of validation you would like to use.")

    # validate sample weights if not None
    if sample_weight is not None:
        _check_sample_weight(X, sample_weight, "X",
                             "sample_weight", automl_settings)

    if X_valid is not None and y_valid is None:
        raise ValueError(
            "X validation provided but y validation data is missing.")

    if y_valid is not None and X_valid is None:
        raise ValueError(
            "y validation provided but X validation data is missing.")

    if X_valid is not None and sample_weight is not None and \
            sample_weight_valid is None:
        raise ValueError("sample_weight_valid should be set to a valid value")

    if sample_weight_valid is not None and X_valid is None:
        raise ValueError(
            "sample_weight_valid should only be set if X_valid is set")

    if sample_weight_valid is not None:
        _check_sample_weight(X_valid, sample_weight_valid,
                             "X_valid", "sample_weight_valid", automl_settings)

    _check_dimensions(
        X=X, y=y, X_valid=X_valid, y_valid=y_valid,
        sample_weight=sample_weight, sample_weight_valid=sample_weight_valid)

    if X_valid is not None:
        if automl_settings.n_cross_validations is not None and \
                automl_settings.n_cross_validations > 0:
            raise ValueError("Both custom validation data and "
                             "n_cross_validations specified. "
                             "If you are providing the training "
                             "data, do not pass any n_cross_validations.")
        if automl_settings.validation_size is not None and \
                automl_settings.validation_size > 0.0:
            raise ValueError("Both custom validation data and "
                             "validation_size specified. If you are "
                             "providing the training data, do not pass "
                             "any validation_size.")

        if automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            # y_valid should be a subset of y(training sample) for certain primary
            # metrics
            primary_metric = automl_settings.primary_metric
            validation_sensitive_primary_metrics = [constants.Metric.AUCWeighted,
                                                    constants.Metric.AvgPrecisionWeighted,
                                                    constants.Metric.NormMacroRecall]
            if primary_metric in validation_sensitive_primary_metrics:
                in_train = set(y)
                in_valid = set(y_valid)
                only_in_valid = in_valid - in_train
                if len(only_in_valid) > 0:
                    raise ValueError(
                        "y values in validation set should be a subset of "
                        "y values of training set for metrics {metrics}.".format(
                            metrics=validation_sensitive_primary_metrics))

    if cv_splits_indices is not None:
        if automl_settings.n_cross_validations is not None and \
                automl_settings.n_cross_validations > 0:
            raise ValueError("Both cv_splits_indices and n_cross_validations "
                             "specified. If you are providing the indices to "
                             "use to split your data. Do not pass any "
                             "n_cross_validations.")
        if automl_settings.validation_size is not None and \
                automl_settings.validation_size > 0.0:
            raise ValueError("Both cv_splits_indices and validation_size "
                             "specified. If you are providing the indices to "
                             "use to split your data. Do not pass any "
                             "validation_size.")
        if X_valid is not None:
            raise ValueError("Both cv_splits_indices and custom split "
                             "validation data specified. If you are providing "
                             "the training data, do not pass any indices to "
                             "split your data.")

    if automl_settings.model_explainability and X_valid is None:
        raise ValueError("Model explainability does not support if n_cross_validations "
                         "or cv_splits_indices specified. If you enabled model_explainability, "
                         "please provide X_valid data.")


def _validate_data_splits(X, y, X_valid, y_valid, cv_splits, automl_settings):
    """
    Validate data splits.

    Validate Train-Validation-Test data split and raise error if the data split is expected to fail all the child runs.
    This will gracefully fail the ParentRun in case of Local target and the SetupRun in case of the Remote target.
    :param X: Training data.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y: Training labels.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param X_valid: validation features.
    :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param y_valid: validation labels.
    :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
    :param cv_splits: cross-validation split object training/validation/test data splits for different
        types of cross validation.
    :type cv_splits: automl.client.core.common._cv_splits
    :param automl_settings: The settings object used for this current run
    :return:
    """
    if cv_splits:
        cv_splits_indices = cv_splits.get_cv_split_indices()
        train_indices, _, valid_indices = cv_splits.get_train_test_valid_indices()
    else:
        cv_splits_indices, train_indices, valid_indices = None, None, None
    task_type = automl_settings.task_type
    if task_type == constants.Tasks.CLASSIFICATION:
        primary_metric = automl_settings.primary_metric
        all_primary_metrics = _get_primary_metrics(task_type)
        validation_sensitive_primary_metrics = [constants.Metric.AUCWeighted,
                                                constants.Metric.AvgPrecisionWeighted,
                                                constants.Metric.NormMacroRecall]
        if primary_metric in validation_sensitive_primary_metrics:
            error_msg = ""
            if y_valid is not None:
                missing_validation_classes = np.setdiff1d(np.unique(y), np.unique(y_valid))
                if len(missing_validation_classes) > 0:
                    error_msg += "y_valid is missing samples from the following classes: {classes}.\n"\
                        .format(classes=missing_validation_classes)
            elif cv_splits_indices is not None:
                for k, splits in enumerate(cv_splits_indices):
                    missing_validation_classes = np.setdiff1d(np.unique(y[splits[0]]), np.unique(y[splits[1]]))
                    if len(missing_validation_classes) > 0:
                        error_msg += \
                            "{k} validation split is missing samples from the following classes: {classes}.\n"\
                            .format(k=_ordinal_string(k), classes=missing_validation_classes)
            elif valid_indices is not None:
                missing_validation_classes = np.setdiff1d(np.unique(y[train_indices]), np.unique(y[valid_indices]))
                if len(missing_validation_classes) > 0:
                    error_msg += "Validation data is missing samples from the following classes: {classes}.\n"\
                        .format(classes=missing_validation_classes)

            if error_msg:
                raise ValueError("Train-Validation Split Error:\n"
                                 "{msg}"
                                 "{primary_metric} cannot be calculated for this validation data. "
                                 "Please use one of the following primary metrics: {accepted_metrics}."
                                 .format(msg=error_msg,
                                         primary_metric=primary_metric,
                                         accepted_metrics=np.setdiff1d(all_primary_metrics,
                                                                       validation_sensitive_primary_metrics)))


def _validate_training_data_dict(data_dict, automl_settings):
    _validate_training_data(*_data_dict_to_tuple(data_dict), automl_settings)


def _data_dict_to_tuple(data_dict):
    X = data_dict.get('X', None)
    y = data_dict.get('y', None)
    sample_weight = data_dict.get('sample_weight', None)
    X_valid = data_dict.get('X_valid', None)
    y_valid = data_dict.get('y_valid', None)
    sample_weight_valid = data_dict.get('sample_weight_valid', None)
    cv_splits_indices = data_dict.get('cv_splits_indices', None)
    return X, y, X_valid, y_valid, sample_weight, sample_weight_valid, cv_splits_indices


def friendly_http_exception(exception, api_name):
    """
    Friendly exceptions for a http exceptions.

    :param exception: Exception.
    :param api_name: string.
    :raise: ServiceException
    """
    try:
        # Raise bug with msrest team that response.status_code is always 500
        status_code = exception.error.response.status_code
        if status_code == 500:
            message = exception.message
            substr = 'Received '
            status_code = message[message.find(
                substr) + len(substr): message.find(substr) + len(substr) + 3]
    except Exception:
        raise exception

    if status_code in _constants_azureml.HTTP_ERROR_MAP:
        http_error = _constants_azureml.HTTP_ERROR_MAP[status_code]
    else:
        http_error = _constants_azureml.HTTP_ERROR_MAP['default']
    if api_name in http_error:
        error_message = http_error[api_name]
    else:
        error_message = http_error['default']
    raise ServiceException("{0} error raised. {1}".format(
        http_error['Name'], error_message)) from exception


def _get_primary_metrics(task):
    """
    Get the primary metrics supported for a given task as a list.

    :param task: string "classification" or "regression".
    :return: A list of the primary metrics supported for the task.
    """
    if task == constants.Tasks.CLASSIFICATION:
        return list(constants.Metric.CLASSIFICATION_PRIMARY_SET)
    elif task == constants.Tasks.REGRESSION:
        return list(constants.Metric.REGRESSION_PRIMARY_SET)
    else:
        raise NotImplemented("Task {task} is not supported currently."
                             .format(task=task))


def _auto_blacklist(input_data, automl_settings):
    """
    Add appropriate files to blacklist automatically.

    :param input_data:
    :param automl_settings: The settings used for this current run.
    :return:
    """
    if automl_settings.auto_blacklist:
        X = input_data['X']
        if scipy.sparse.issparse(X) or len(X) > constants.MAX_SAMPLES_BLACKLIST:
            if automl_settings.blacklist_algos is None:
                automl_settings.blacklist_algos = \
                    constants.MAX_SAMPLES_BLACKLIST_ALGOS
            else:
                for blacklist_algo in constants.MAX_SAMPLES_BLACKLIST_ALGOS:
                    if blacklist_algo not in automl_settings.blacklist_algos:
                        automl_settings.blacklist_algos.append(blacklist_algo)
            automl_settings.blacklist_samples_reached = True


def _set_task_parameters(y, automl_settings):
    """
    Set this task's parameters based on some heuristics if they aren't provided.

    :param automl_settings: The settings used for this current run
    :param y: The list of possible output values
    :return:
    """
    if automl_settings.task_type == constants.Tasks.CLASSIFICATION:
        #  Guess number of classes if the user did not explicitly provide it
        if not automl_settings.num_classes or not isinstance(
                automl_settings.num_classes, int):
            automl_settings.num_classes = len(np.unique(y))
        return

    if automl_settings.task_type == constants.Tasks.REGRESSION:
        numpy_unserializable_ints = (np.int8, np.int16, np.int32, np.int64,
                                     np.uint8, np.uint16, np.uint32, np.uint64)

        #  Guess min and max of y if the user did not explicitly provide it
        if not automl_settings.y_min or not isinstance(automl_settings.y_min,
                                                       float):
            automl_settings.y_min = np.min(y)
            if isinstance(automl_settings.y_min, numpy_unserializable_ints):
                automl_settings.y_min = int(automl_settings.y_min)
        if not automl_settings.y_max or not isinstance(automl_settings.y_max,
                                                       float):
            automl_settings.y_max = np.max(y)
            if isinstance(automl_settings.y_max, numpy_unserializable_ints):
                automl_settings.y_max = int(automl_settings.y_max)
        assert automl_settings.y_max != automl_settings.y_min
        return
    raise NotImplementedError()


def _get_ts_params_dict(automl_settings):
    if automl_settings.is_timeseries:
        return {
            constants.TimeSeries.TIME_COLUMN_NAME: automl_settings.time_column_name,
            constants.TimeSeries.GRAIN_COLUMN_NAMES: automl_settings.grain_column_names,
            constants.TimeSeries.DROP_COLUMN_NAMES: automl_settings.drop_column_names
        }
    else:
        return None


def _ordinal_string(integer):
    return "%d%s" % (integer, "tsnrhtdd"[(integer / 10 % 10 != 1) * (integer % 10 < 4) * integer % 10::4])


def _log_user_sdk_dependencies(run, logger):
    """
    Log the AzureML packages currently installed on the local machine to the given run.

    :param run: The run to log user depenencies.
    :param logger: The logger to write user dependencies.
    :return:
    :type: None
    """
    dependencies = {'dependencies_versions': json.dumps(get_sdk_dependencies())}
    logger.info("[RunId:{}]SDK dependencies versions:{}."
                .format(run.id, dependencies['dependencies_versions']))
    run.add_properties(dependencies)


def _sanitize_fit_output(fit_output):
    """
    Sanitize fit output so that every value is a string.

    :param fit_output: the dictionary that should be sanitized
    :return: a dictionary with all values converted to strings
    """
    fit_output_str = {}
    for key in fit_output:
        if fit_output[key] is None:
            fit_output_str[key] = ''
        else:
            # Cast to string to avoid warnings (PR 143137)
            fit_output_str[key] = str(fit_output[key])
    return fit_output_str
