# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities used during AutoML training."""
import numpy as np
import pandas as pd
import scipy

from . import constants
from . import dataprep_utilities
from . import utilities
from . import _engineered_feature_names
from .automl_base_settings import AutoMLBaseSettings


def auto_blacklist(input_data, automl_settings):
    """
    Add appropriate files to blacklist automatically.

    :param input_data:
    :param automl_settings: The settings used for this current run.
    :return:
    """
    if automl_settings.auto_blacklist:
        X = input_data['X']
        if scipy.sparse.issparse(X) or X.shape[0] > constants.MAX_SAMPLES_BLACKLIST:
            if automl_settings.blacklist_algos is None:
                automl_settings.blacklist_algos = \
                    constants.MAX_SAMPLES_BLACKLIST_ALGOS
            else:
                for blacklist_algo in constants.MAX_SAMPLES_BLACKLIST_ALGOS:
                    if blacklist_algo not in automl_settings.blacklist_algos:
                        automl_settings.blacklist_algos.append(blacklist_algo)
            automl_settings.blacklist_samples_reached = True


def set_task_parameters(y, automl_settings):
    """
    Set this task's parameters based on some heuristics if they aren't provided.

    TODO: Move this code into AutoML settings or something. Client shouldn't have to think about this stuff.

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


def format_training_data(
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
            data_dict = utilities.extract_user_data(user_script)
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
            X = dataprep_utilities.try_retrieve_pandas_dataframe(X)
            y = dataprep_utilities.try_retrieve_numpy_array(y)
            sample_weight = dataprep_utilities.try_retrieve_numpy_array(
                sample_weight)
            X_valid = dataprep_utilities.try_retrieve_pandas_dataframe(
                X_valid)
            y_valid = dataprep_utilities.try_retrieve_numpy_array(y_valid)
            sample_weight_valid = dataprep_utilities.try_retrieve_numpy_array(
                sample_weight_valid)
            cv_splits_indices = dataprep_utilities.try_resolve_cv_splits_indices(
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


def validate_training_data(X,
                           y,
                           X_valid,
                           y_valid,
                           sample_weight,
                           sample_weight_valid,
                           cv_splits_indices,
                           automl_settings: AutoMLBaseSettings):
    """
    Validate that training data and parameters have been correctly provided.

    :param X:
    :param y:
    :param X_valid:
    :param y_valid:
    :param sample_weight:
    :param sample_weight_valid:
    :param cv_splits_indices:
    :param automl_settings:
    """
    check_x_y(X, y, automl_settings)

    # Ensure at least one form of validation is specified
    if not ((X_valid is not None) or automl_settings.n_cross_validations or
       (cv_splits_indices is not None) or automl_settings.validation_size):
        raise ValueError(
            "No form of validation was provided. Please specify the data "
            "or type of validation you would like to use.")

    # validate sample weights if not None
    if sample_weight is not None:
        check_sample_weight(X, sample_weight, "X",
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
        check_sample_weight(X_valid, sample_weight_valid,
                            "X_valid", "sample_weight_valid", automl_settings)

    utilities._check_dimensions(
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


def validate_training_data_dict(data_dict, automl_settings):
    """
    Validate that training data and parameters have been correctly provided.

    :param data_dict:
    :param automl_settings:
    :return:
    """
    X = data_dict.get('X', None)
    y = data_dict.get('y', None)
    sample_weight = data_dict.get('sample_weight', None)
    X_valid = data_dict.get('X_valid', None)
    y_valid = data_dict.get('y_valid', None)
    sample_weight_valid = data_dict.get('sample_weight_valid', None)
    cv_splits_indices = data_dict.get('cv_splits_indices', None)
    validate_training_data(X, y, X_valid, y_valid, sample_weight, sample_weight_valid, cv_splits_indices,
                           automl_settings)


def check_x_y(x,
              y,
              automl_settings: AutoMLBaseSettings):
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
                _engineered_feature_names.FeatureTypeRecognizer.DateTime.lower(),
                _engineered_feature_names.FeatureTypeRecognizer.Categorical.lower(),
                _engineered_feature_names.FeatureTypeRecognizer.Text.lower())

        if isinstance(x, pd.DataFrame):
            for column in x.columns:
                if not utilities._check_if_column_data_type_is_numerical(
                        utilities._get_column_data_type_as_str(x[column].values)):
                    raise ValueError(without_preprocess_error_str)
        elif isinstance(x, np.ndarray):
            if len(x.shape) == 1:
                if not utilities._check_if_column_data_type_is_numerical(
                        utilities._get_column_data_type_as_str(x)):
                    raise ValueError(without_preprocess_error_str)
            else:
                for index in range(x.shape[1]):
                    if not utilities._check_if_column_data_type_is_numerical(
                            utilities._get_column_data_type_as_str(x[:, index])):
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
        if not utilities._check_if_column_data_type_is_numerical(
                utilities._get_column_data_type_as_str(y)):
            raise ValueError(
                "Please make sure y is numerical before fitting for "
                "regression")


def check_sample_weight(x,
                        sample_weight,
                        x_name: str,
                        sample_weight_name: str,
                        automl_settings: AutoMLBaseSettings):
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
            constants.Metric.SAMPLE_WEIGHTS_UNSUPPORTED_SET:
        raise ValueError("Sample weights is not supported for these primary metrics: {0}"
                         .format(constants.Metric.SAMPLE_WEIGHTS_UNSUPPORTED_SET))


def validate_data_splits(X, y, X_valid, y_valid, cv_splits, primary_metric, task_type):
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
    :param primary_metric: The primary metric for this run
    :param task_type: The task type for this run
    :return:
    """
    if cv_splits:
        cv_splits_indices = cv_splits.get_cv_split_indices()
        train_indices, _, valid_indices = cv_splits.get_train_test_valid_indices()
    else:
        cv_splits_indices, train_indices, valid_indices = None, None, None

    if task_type == constants.Tasks.CLASSIFICATION:
        all_primary_metrics = utilities.get_primary_metrics(task_type)
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
                            .format(k=utilities.to_ordinal_string(k), classes=missing_validation_classes)
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
