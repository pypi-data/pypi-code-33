# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Global methods used during an AutoML fit method for pre-processing raw data into meaningful features."""
import math
import json
import re
from functools import wraps
from collections import defaultdict

import dateutil
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import murmurhash3_32
from sklearn_pandas import DataFrameMapper

from automl.client.core.common import constants
from automl.client.core.common import utilities
from automl.client.core.common._engineered_feature_names import \
    _GenerateEngineeredFeatureNames, \
    _TransformationFunctionNames, _OperatorNames, \
    FeatureTypeRecognizer, _Transformer, \
    _FeatureTransformers


def function_debug_log_wrapped(f):
    """Add logs wrapper around transformer class function."""
    @wraps(f)
    def debug_log_wrapped(self, *args, **kwargs):
        self._logger_wrapper(
            "debug", "[Class:{}][Function:{}] Started.".format(
                self.__class__.__name__, f.__name__
            )
        )
        r = f(self, *args, **kwargs)
        self._logger_wrapper(
            "debug", "[Class:{}][Function:{}] Ended.".format(
                self.__class__.__name__, f.__name__
            )
        )
        return r

    return debug_log_wrapped


class TransformerLogger(object):
    """Base logger class for all the transformers."""

    def __init__(self):
        """Init the logger class."""
        self.logger = None

    def __getstate__(self):
        """
        Overriden to remove logger object when pickling.

        :return: this object's state as a dictionary
        """
        state = self.__dict__.copy()
        state['logger'] = None
        return state

    def _init_logger(self, logger):
        """
        Init the logger.

        :param logger: the logger handle.
        :type logger: logging.Logger.
        """
        self.logger = logger

    def _logger_wrapper(self, level, message):
        """
        Log a message with a given debug level in a log file.

        :param logger: the logger handle
        :type logger: logging.Logger
        :param level: log level (info or debug)
        :param message: log message
        :type message: str
        """
        # Check if the logger object is valid. If so, log the message
        # otherwise pass
        if self.logger is not None:
            if level == 'info':
                self.logger.info(message)
            elif level == 'warning':
                self.logger.warning(message)
            elif level == 'debug':
                self.logger.debug(message)


class BinTransformer(BaseEstimator, TransformerMixin, TransformerLogger):
    """
    Wrapper over pandas.cut for binning the train data into intervals and then applying them to test data.

    :param num_bins: Number of bins for binning the values into discrete
    intervals.
    :type num_bins: int
    """

    def __init__(self, num_bins=5, logger=None):
        """
        Construct the BinTransformer.

        :param num_bins: Number of bins for binning the values into discrete
        intervals.
        :type num_bins: int
        """
        self._num_bins = num_bins
        self._bins = None
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Identify the distribution of values with repect to the number of specified bins.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The transformed data.
        """
        _, self._bins = pd.cut(x, self._num_bins, retbins=True)
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Return the bins identified for the input values.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.series
        :return: The transformed data.
        """
        if self._bins is None:
            raise ValueError("BinTransformer not fit")
        return pd.cut(x, bins=self._bins, labels=False)


class NaiveBayes(BaseEstimator, TransformerMixin, TransformerLogger):
    """Wrapper for sklearn Multinomial Naive Bayes."""

    def __init__(self, logger=None):
        """Construct the Naive Bayes transformer."""
        self.model = MultinomialNB()
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Naive Bayes transform to learn conditional probablities for textual data.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Naive Bayes class object.
        """
        self.model.fit(x, y)
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform data x.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.series
        :return: Prediction probability values from Naive Bayes model.
        """
        return self.model.predict_proba(x)


class ImputationMarker(BaseEstimator, TransformerMixin, TransformerLogger):
    """Add boolean imputation marker for values that are imputed."""

    def __init__(self, logger=None):
        """Initialize the Logger object."""
        self.logger = logger

    def fit(self, x, y=None):
        """
        Fit function for imputation marker transform.

        :param x: Input array of integers or strings.
        :type x: numpy.ndarray or pandas.series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform function for imputation marker.

        :param x: Input array of integers or strings.
        :type x: numpy.ndarray or pandas.series
        :return: Boolean array having True where the value is not present.
        """
        return pd.isnull(x).values


class CatImputer(BaseEstimator, TransformerMixin, TransformerLogger):
    """
    Impute missing values for categorical data by the most frequent category.

    :param copy: Create copy of the categorical column.
    :type copy: boolean
    """

    def __init__(self, copy=True, logger=None):
        """
        Construct the CatImputer.

        :param copy: Create copy of the categorical column.
        :type copy: boolean
        :return:
        """
        self._missing_vals = [np.nan]
        self._copy = copy
        self._init_logger(logger)

    def _get_mask(self, x):
        """
        Get missing values mask.

        :param x: Input array.
        :return: Mask with missing values.
        """
        mask = np.zeros(x.shape, dtype=bool)
        x_object = None
        for val in self._missing_vals:
            if val is None or (isinstance(val, float) and np.isnan(val)):
                mask = mask | pd.isnull(x)
            else:
                x_object = x.astype(
                    np.object) if x_object is None else x_object
                mask = mask | (x_object == val)

        return mask

    def fit(self, x, y=None):
        """
        Transform the data to mark the missing values and identify the most frequent category.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: The transformed data.
        """
        non_na = x.dropna()
        if non_na.empty:
            self._fill = str(np.nan)
            return self

        series_name = x.name if x.name is not None else 0

        mode = non_na.to_frame().groupby(series_name)[
            series_name].agg("count").idxmax()
        self._fill = mode

        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform data x by adding the missing values with the most frequent categories.

        Must call fit() before calling transform()

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.series
        :return: The transformed data.
        """
        if self._fill is None:
            raise ValueError("CatImputer fit not called")

        mask = self._get_mask(x)
        if self._copy:
            x = x.copy()
        x[mask] = self._fill

        return x.values


class DateTimeFeaturesTransformer(BaseEstimator,
                                  TransformerMixin, TransformerLogger):
    """
    Expands datetime features from input into sub features.

    Like year, month, day, day of the week, day of the year, quarter, week of
    the month, hour, minute and second.
    """

    def __init__(self, logger=None):
        """Initilize the logger."""
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Fit function for date time transform.

        :param x: Input array.
        :type x: numpy.ndarray or pandas.series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform data x.

        :param x: The data to transform.
        :type x: numpy.ndarray or pandas.series
        :return: The transformed data.
        """
        return self._datetime_feats(x)

    def _datetime_feats(self, x):
        """
        Get the features for a datetime column.

        Expand the date time features from array of dates.

        :param x: Series that represents column.
        :type x: numpy.ndarray or pandas.series
        :return: Features for datetime column.
        """
        x = pd.to_datetime(pd.Series(x), infer_datetime_format=True,
                           box=False, errors="coerce").fillna(pd.Timestamp.min)
        return pd.concat([
            x.dt.year,
            x.dt.month,
            x.dt.day,
            x.dt.dayofweek,
            x.dt.dayofyear,
            x.dt.quarter,
            x.apply(lambda dt: (dt.day - 1) // 7 + 1),
            x.dt.hour,
            x.dt.minute,
            x.dt.second,
        ], axis=1).values


class HashOneHotVectorizerTransformer(BaseEstimator,
                                      TransformerMixin,
                                      TransformerLogger):
    """
    Convert input to hash and encode to one hot encoded vector.

    The input and output type is same for this transformer.

    :param hashing_seed_val: Seed value for hashing transform.
    :type hashing_seed_val: int
    :param num_cols: Number of columns to be generated.
    :type num_cols: int
    """

    def __init__(self, hashing_seed_val, num_cols=8096, logger=None):
        """
        Initialize for hashing one hot encoder transform with a seed value and maximum number of expanded columns.

        :param hashing_seed_val: Seed value for hashing transform.
        :type hashing_seed_val: int
        :param num_cols: Number of columns to be generated.
        :type num_cols: int
        :return:
        """
        self._num_cols = num_cols
        self._seed = hashing_seed_val
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Fit function for hashing one hot encoder transform.

        :param x: Input array.
        :type x: numpy.ndarray or pandas.series
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    def _hash_cat_feats(self, x):
        """
        Hash transform and one-hot encode the input series or dataframe.

        :param x: Series that represents column.
        :type x: numpy.ndarray or pandas.series
        :return: Hash vector features for column.
        """
        row = []
        col = []
        data = []
        row_no = 0
        for val in x:
            hash_val = murmurhash3_32(val, self._seed) % self._num_cols
            row.append(row_no)
            row_no = row_no + 1
            col.append(hash_val)
            data.append(True)

        X = sparse.csr_matrix((data, (row, col)),
                              shape=(x.shape[0], self._num_cols),
                              dtype=np.bool_)
        X.sort_indices()
        return X

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform function for hashing one hot encoder transform.

        :param x: Input array.
        :type x: numpy.ndarray or pandas.series
        :return: Result of hashing one hot encoder transform.
        """
        return self._hash_cat_feats(x)


class StringCastTransformer(BaseEstimator,
                            TransformerMixin,
                            TransformerLogger):
    """
    Cast input to string.

    The input and output type is same for this transformer.
    """

    def __init__(self, logger=None):
        """Initialize the Logger object."""
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Fit function for string cast transform.

        :param x: Input array.
        :type x: numpy.ndarray
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform data x into array of strings.

        :param x: The data to transform.
        :type x: numpy.ndarray
        :return: The transformed data which is an array of strings.
        """
        return x.astype(str)


class LambdaTransformer(BaseEstimator, TransformerMixin, TransformerLogger):
    """
    Transforms column through a lambda function.

    :param func: The lambda function to use in the transformation.
    :type func: function
    """

    def __init__(self, func, logger=None):
        """
        Construct the LambdaTransformer.

        :param func: The lambda function to use in the transformation.
        :type func: function
        :return:
        """
        self.func = func
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Fit function for lambda transform.

        :param x: Input array.
        :type x: numpy.ndarray
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Lambda transform which calls the lambda function over the input.

        :param x: Input array.
        :type x: numpy.ndarray
        :return: Result of lambda transform.
        """
        return self.func(x)


class LabelEncoderTransformer(BaseEstimator,
                              TransformerMixin,
                              TransformerLogger):
    """
    Transforms column using a label encoder to encode categories into numbers.

    :param hashing_seed_val: Seed value used for hashing if needed.
    :type hashing_seed_val: int
    """

    def __init__(self, hashing_seed_val, logger=None):
        """
        Initialize for label encoding transform.

        :param hashing_seed_val: Seed value used for hashing if needed.
        :type hashing_seed_val: int
        :return:
        """
        self._label_encoder = LabelEncoder()
        self._hashing_seed_val = hashing_seed_val
        self._init_logger(logger)

    def fit(self, x, y=None):
        """
        Fit function for label encoding transform which learns the labels.

        :param x: Input array of integers or strings.
        :type x: numpy.ndarray
        :param y: Target values.
        :type y: numpy.ndarray
        :return: Class object itself.
        """
        # Keep track of the labels
        self._label_encoder.fit(x)
        return self

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Label encoding transform categorical data into integers.

        :param x: Input array of integers or strings.
        :type x: numpy.ndarray
        :return: Label encoded array of ints.
        """
        # Find the new classes in 'x'
        new_classes = np.unique(x)

        # Check if new classes are being label encoded
        if len(
                np.intersect1d(
                    new_classes,
                    self._label_encoder.classes_)) < len(new_classes):

            # Create a set of new classes that are detected
            new_classes = np.setdiff1d(new_classes,
                                       self._label_encoder.classes_)

            # Walk each entry in x and map the new classes to existing classes
            x_new_with_known_classes = []
            for entry in x:
                if entry in new_classes:
                    # Compute the hash for the entry and then map it to some
                    # existing class
                    entry = self._label_encoder.classes_[
                        (murmurhash3_32(entry,
                                        seed=self._hashing_seed_val)) % len(
                            self._label_encoder.classes_)]

                x_new_with_known_classes.append(entry)

            # It is safe to run label encoder on all the existing classes
            return self._label_encoder.transform(x_new_with_known_classes)

        # Label encode x column
        return self._label_encoder.transform(x)


class RawFeatureStats:
    """
    Class for computing feature stats from raw features.

    :param raw_column: Column having raw data.
    :type raw_column: numpy.ndarray
    """

    def __init__(self, raw_column):
        """
        Calculate stats for the input column.

        These stats are needed for deciding the data type of the column.

        :param raw_column: Column having raw data.
        :type raw_column: numpy.ndarray
        """
        # Regular expressions for date time detection
        self.date_regex1 = re.compile(r'(\d+/\d+/\d+)')
        self.date_regex2 = re.compile(r'(\d+-\d+-\d+)')

        # Number of unique values in the column
        self.num_unique_vals = raw_column.unique().shape[0]
        # Total number of values in the column
        self.total_number_vals = raw_column.shape[0]
        # Create a series having lengths of the entries in the column
        self.lengths = raw_column.apply(str).apply(len)
        # Calculate the number of lengths of the entries in the column
        self.num_unique_lens = self.lengths.unique().shape[0]
        # Get the column type
        self.column_type = utilities.\
            _get_column_data_type_as_str(raw_column.values)
        # Average lengths of an entry in the column
        self.average_entry_length = 0
        # Average number of spaces in an entry in the column
        self.average_number_spaces = 0
        # Number of missing values in the column
        self.num_na = raw_column.isnull().sum()

        # Detect if the column has date time format
        non_na = raw_column.dropna()
        num_dates = np.sum(non_na.apply(str).apply(self._is_date))
        self.is_datetime = False
        if num_dates == non_na.shape[0] and non_na.shape[0] > 0:
            self.is_datetime = True

        for column_entry in raw_column:
            # if not np.isnan(column_entry):
            self.average_entry_length += len(str(column_entry))
            self.average_number_spaces += str(column_entry).count(' ')

        self.average_entry_length /= 1.0 * self.total_number_vals
        self.average_number_spaces /= 1.0 * self.total_number_vals

        self.cardinality_ratio = \
            (1.0 * self.num_unique_vals) / self.total_number_vals

    def _is_date(self, input):
        """
        Check if a given string is a date.

        Needs regex to make sure the dateutil doesn't allow integers
        interpreted as epochs.

        :param input: String.
        :return: True/False.
        """
        if (self.date_regex1.search(input) is None and
                self.date_regex2.search(input) is None):
            return False

        try:
            dateutil.parser.parse(input)
            return True
        except ValueError:
            return False


class _PreprocessingStatistics:
    """
    Keeps statistics about the pre-processing stage in AutoML.

    Records the number of various feature types detected from
    the raw data
    """

    def __init__(self):
        """Initialize all statistics about the raw data."""
        # Dictionary to capture all raw feature stats
        self.num_raw_feature_type_detected = defaultdict(int)

    def update_raw_feature_stats(self, feature_type):
        """Increment the counters for different types of features."""
        if feature_type in FeatureTypeRecognizer.FULL_SET:
            self.num_raw_feature_type_detected[feature_type] += 1

    def get_raw_data_stats(self):
        """Return the string for overall raw feature stats."""
        str_overall_raw_stats = 'The stats for raw data are following:-'
        for feature_type in FeatureTypeRecognizer.FULL_SET:
            str_overall_raw_stats += \
                '\n\tNumber of ' + feature_type + ' features: ' + \
                str(self.num_raw_feature_type_detected[feature_type])

        return str_overall_raw_stats


class DataTransformer(BaseEstimator, TransformerMixin, TransformerLogger):
    """
    Preprocessing class that can be added in pipeline for input.

    This class does the following:
    1. Numerical inputs treated as it is.
    2. For dates: year, month, day and hour are features
    3. For text, tfidf features
    4. Small number of unique values for a column that is not float become
        categoricals

    :param task: 'classification' or 'regression' depending on what kind of
    ML problem to solve.
    :type task: str or automl.client.core.common.constants.Tasks
    """

    def __init__(self, task=constants.Tasks.CLASSIFICATION, logger=None):
        """
        Initialize for data transformer for pre-processing raw user data.

        :param task: 'classification' or 'regression' depending on what kind
        of ML problem to solve.
        :type task: str or azureml.train.automl.constants.Tasks
        :param logger: External logger handler.
        :type logger: logging.Logger
        """
        if task not in \
                [constants.Tasks.CLASSIFICATION, constants.Tasks.REGRESSION]:
            raise ValueError("Unknown task")

        self._task_type = task
        self.mapper = None

        # ratio of unique values to total values to be considered categoricals
        self._min_ratio_uniq_cats = 0.05
        # max number of unique values to be considered cats
        self._max_num_cats = 200
        # max number of unique values to be considered categorical hash
        self._max_num_cat_hash = 10000
        # max number of unique values to be considered cats for integer
        self._max_num_cats_int = 50
        # ratio of unique values to total values to be considered hashes
        self._min_ratio_hashes = 0.9
        # number of maxrows allowed for tfidf computation since tfidf
        # vectorizer is expensive
        self._maxrows_for_tfidf = 1e5
        # max number of unique lengths in a column to be considered hash
        self._max_uniqhashlens = 3
        # min number of rows for hashes to be present
        self._min_num_hashrows = 200
        # max size in characters for ngram
        self._max_ngram = 3
        # Hashing seed value for murmurhash
        self._hashing_seed_value = 314489979
        # External logger if None, then no logs
        self._init_logger(logger)
        # Maintain a list of raw feature names
        self._raw_feature_names = []
        # Maintain engineered feature name class
        self._engineered_feature_names_class = None
        # Maintain statistics about the pre-processing stage
        self._pre_processing_stats = _PreprocessingStatistics()

    def _learn_transformations(self, df, y=None):
        """
        Learn data transformation to be done on the raw data.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: numpy.ndarray or pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray or pandas.DataFrame
        """
        self._check_input(df)
        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        if self._engineered_feature_names_class is None:
            # Create class for engineered feature names
            self._engineered_feature_names_class = \
                _GenerateEngineeredFeatureNames()

        self.mapper = DataFrameMapper(
            self._get_transforms(df), input_df=True, sparse=True)

    def fit_transform_with_logger(self, X, y=None, logger=None, **fit_params):
        """
        Wrap the fit_transform function for the Data transformer class.

        :param X: Dataframe representing text, numerical or categorical input.
        :type X:numpy.ndarray or pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray or pandas.DataFrame
        :param fit_params: Additional parameters for fit_transform().
        :param logger: External logger handler.
        :type logger: logging.Logger
        :return: Transformed data.
        """
        # Init the logger
        self.logger = logger
        # Call the fit and transform function
        return self.fit_transform(X, y, **fit_params)

    def fit(self, df, y=None):
        """
        Perform the raw data validation and identify the transformations to apply.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: numpy.ndarray or pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray or pandas.DataFrame
        :return: DataTransform object.
        :raises: Value Error for non-dataframe and empty dataframes.
        """
        self._check_input(df)
        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        if not self.mapper:
            self._logger_wrapper(
                'info', 'Featurizer mapper not found so learn all ' +
                'the transforms')
            self._learn_transformations(df, y)

        self.mapper.fit(df, y)

        return self

    @function_debug_log_wrapped
    def transform(self, df):
        """
        Transform the input raw data with the transformations idetified in fit stage.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: numpy.ndarray or pandas.DataFrame
        :return: Numpy array.
        """
        if not self.mapper:
            raise Exception("fit not called")

        self._check_input(df)

        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        transformed_data = self.mapper.transform(df)

        if self._engineered_feature_names_class is not None:
            if not self._engineered_feature_names_class.\
                    are_engineered_feature_names_available():
                # Generate engineered feature names if they are
                # not alreadt generated
                self._engineered_feature_names_class.\
                    parse_raw_feature_names(
                        self.mapper.transformed_names_)

        return transformed_data

    def get_engineered_feature_names(self):
        """
        Get the engineered feature names.

        Return the list of engineered feature names as string after data transformations on the
        raw data have been finished.

        :return: The list of engineered fearure names as strings
        """
        return self._engineered_feature_names_class.\
            _engineered_feature_names

    def _get_json_str_for_engineered_feature_name(self,
                                                  engineered_feature_name):
        """
        Return JSON string for engineered feature name.

        :param engineered_feature_name: Engineered feature name for
                                        whom JSON string is required
        :return: JSON string for engineered feature name
        """
        engineered_feature_name_json_obj = \
            self._engineered_feature_names_class.\
            get_json_object_for_engineered_feature_name(
                engineered_feature_name)

        # If the JSON object is not valid, then return None
        if engineered_feature_name_json_obj is None:
            self._logger_wrapper(
                'info', "Not a valid feature name " + engineered_feature_name)
            return None

        # Convert JSON into string and return
        return json.dumps(engineered_feature_name_json_obj)

    def get_json_strs_for_engineered_feature_names(self,
                                                   engi_feature_name_list):
        """
        Return JSON string list for engineered feature names.

        :param engi_feature_name_list: Engineered feature names for
                                       whom JSON strings are required
        :return: JSON string list for engineered feature names
        """
        engineered_feature_names_json_str_list = []

        # Walk engineering feature name list and get the corresponding
        # JSON string
        for engineered_feature_name in engi_feature_name_list:

            json_str = \
                self._get_json_str_for_engineered_feature_name(
                    engineered_feature_name)

            if json_str is not None:
                engineered_feature_names_json_str_list.append(json_str)

        # Return the list of JSON strings for engineered feature names
        return engineered_feature_names_json_str_list

    def _get_transforms(self, df):
        """
        Identify the transformations for all the columns in the dataframe.

        :param df: Input dataframe.
        :type df: numpy.ndarray or pandas.DataFrame
        :return: Transformations that go into datamapper.
        """
        transforms = []

        # drop columns that have only missing data
        df = df.dropna(axis=1, how="all")

        # In case column names are not specified by the user,
        # append the some column name with a counter to generate a
        # raw feature name
        column_name = 'C'
        index_raw_columns = 0

        self._logger_wrapper('info', "Start getting transformers.")
        for dtype, column in zip(df.dtypes, df.columns):

            # If column name is not an integer, then record it
            # in the raw feature name
            if not isinstance(column, (int, np.integer)):
                self._raw_feature_names.append(column)
                new_column_name = column
            else:
                # If the column name is missing, create a new column name
                # for the transformations
                index_raw_columns += 1
                new_column_name = column_name + str(index_raw_columns)

            # Get stats for the current column
            raw_stats, feature_type_detected = self._detect_feature_type(
                column,
                df)

            utilities._log_raw_data_stat(
                raw_stats, self.logger,
                prefix_message="[XColNum:{}]".format(
                    df.columns.get_loc(column)
                )
            )

            self._logger_wrapper(
                'info',
                "Preprocess transformer for col {}, datatype: {}, detected "
                "datatype {}".format(
                    df.columns.get_loc(column),
                    str(dtype),
                    str(feature_type_detected)
                )
            )

            # Update pre-processing stats
            self._pre_processing_stats.update_raw_feature_stats(
                feature_type_detected)

            if feature_type_detected == FeatureTypeRecognizer.Numeric:
                transforms.extend(self._get_numeric_transforms(
                    column, new_column_name))
                # if there are lot of imputed values, add an imputation marker
                if raw_stats.num_na > 0.01 * raw_stats.total_number_vals:
                    transforms.extend(
                        self._get_imputation_marker_transforms(
                            column, new_column_name))
            elif feature_type_detected == FeatureTypeRecognizer.DateTime:
                transforms.extend(self._get_datetime_transforms(
                    column, new_column_name))
            elif feature_type_detected == \
                    FeatureTypeRecognizer.CategoricalHash:
                transforms.extend(self._get_categorical_hash_transforms(
                    column, new_column_name, raw_stats.num_unique_vals))
            elif feature_type_detected == \
                    FeatureTypeRecognizer.Categorical:
                transforms.extend(self._get_categorical_transforms(
                    column, new_column_name, raw_stats.num_unique_vals))
            elif feature_type_detected == FeatureTypeRecognizer.Text:
                transforms.extend(
                    self._get_text_transforms(
                        column, new_column_name,
                        self._get_ngram_len(raw_stats.lengths)))
            else:
                # skip if hashes or ignore case
                self._logger_wrapper(
                    'info',
                    "Hashes or single value column detected. No transforms "
                    "needed")
                continue

        if not transforms:
            # can happen when we get all hashes
            self._logger_wrapper(
                'warning', "No features could be identified or generated")
            raise ValueError("No features could be identified or generated")

        # Log the transformations done for raw data into the logs
        self._logger_wrapper('info',
                             self._get_transformations_str(df, transforms))

        # Log stats about raw data
        self._logger_wrapper('info',
                             self._pre_processing_stats.get_raw_data_stats())

        self._logger_wrapper('info', "End getting transformers.")

        return transforms

    def _detect_feature_type(self, column, df):
        """
        Calculate the stats on the raw column and decide the data type of the input column.

        :param column: Column name in the data frame.
        :param df: Input dataframe.
        :return: Raw column stats, Type of feature.
        """
        raw_stats = RawFeatureStats(df[column])

        if raw_stats.num_unique_vals == 1:
            # If there is only one unique value, then we don't need to include
            # this column for transformations
            feature_type_detected = FeatureTypeRecognizer.Ignore
        elif raw_stats.is_datetime:
            feature_type_detected = FeatureTypeRecognizer.DateTime
        elif raw_stats.num_unique_vals >= min(
                self._max_num_cats,
                self._min_ratio_uniq_cats * raw_stats.total_number_vals):
            # If number of unique values is higher than a ratio of input data
            if utilities._check_if_column_data_type_is_numerical(
                    raw_stats.column_type):
                feature_type_detected = FeatureTypeRecognizer.Numeric
            else:
                if raw_stats.cardinality_ratio > 0.85 and \
                        raw_stats.average_number_spaces > 1.0:
                    feature_type_detected = FeatureTypeRecognizer.Text
                elif raw_stats.cardinality_ratio < 0.7 and \
                        raw_stats.num_unique_vals < self._max_num_cat_hash:
                    feature_type_detected = \
                        FeatureTypeRecognizer.CategoricalHash
                elif raw_stats.average_number_spaces > 1.0:
                    feature_type_detected = FeatureTypeRecognizer.Text
                elif raw_stats.cardinality_ratio > 0.9:
                    feature_type_detected = FeatureTypeRecognizer.Hashes
                else:
                    feature_type_detected = FeatureTypeRecognizer.Ignore
        else:
            if utilities._check_if_column_data_type_is_int(
                    raw_stats.column_type):
                if raw_stats.num_unique_vals <= min(
                        self._max_num_cats_int,
                        self._min_ratio_uniq_cats *
                        raw_stats.total_number_vals):
                    feature_type_detected = \
                        FeatureTypeRecognizer.Categorical
                else:
                    feature_type_detected = FeatureTypeRecognizer.Numeric
            elif utilities._check_if_column_data_type_is_numerical(
                    raw_stats.column_type):
                feature_type_detected = FeatureTypeRecognizer.Numeric
            else:
                feature_type_detected = FeatureTypeRecognizer.Categorical
        return raw_stats, feature_type_detected

    def _get_ngram_len(self, lens_series):
        """
        Get N-grams length required for text transforms.

        :param lens_series: Series of lengths for a string.
        :return: The ngram to use.
        """
        lens_series = lens_series.apply(lambda x: min(x, self._max_ngram))
        return lens_series.mode()[0]

    def _check_input(self, df):
        """
        Check inputs for transformations.

        :param df: Input dataframe.
        :return:
        """
        # Raise an exception if the input is not a data frame or array
        if not isinstance(df, pd.DataFrame) and not isinstance(df, np.ndarray):
            raise ValueError("df should be a pandas dataframe or numpy array")

    def _get_categorical_hash_transforms(self,
                                         column,
                                         column_name,
                                         num_unique_categories):
        """
        Create a list of transforms for categorical hash data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :param num_unique_categories: Number of unique categories
        :return: Categorical hash transformations to use in a list.
        """
        # Add the transformations to be done and get the alias name
        # for the hashing one hot encode transform.
        categorical_hash_string_cast_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.StringCast,
            operator=None,
            feature_type=FeatureTypeRecognizer.CategoricalHash,
            should_output=False)
        # This transformation depends on the previous# transformation
        categorical_hash_onehot_encode_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=_TransformationFunctionNames.HashOneHotEncode,
            operator=None, feature_type=None,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = \
            _FeatureTransformers(
                [categorical_hash_string_cast_transformer,
                 categorical_hash_onehot_encode_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        alias_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

        # Add the transformations to be done and get the alias name
        # for the raw column.
        number_of_bits = pow(2, int(math.log(num_unique_categories, 2)) + 1)
        tr = [(column, [StringCastTransformer(logger=self.logger),
                        HashOneHotVectorizerTransformer(
                            hashing_seed_val=self._hashing_seed_value,
                            num_cols=int(number_of_bits),
                            logger=self.logger)],
               {'alias': str(alias_column_name)})]

        return tr

    def _get_datetime_transforms(self, column, column_name):
        """
        Create a list of transforms for date time data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :return: Date time transformations to use in a list.
        """
        # Add the transformations to be done and get the alias name
        # for the date time transform.
        datatime_imputer_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.Imputer,
            operator=_OperatorNames.Mode,
            feature_type=FeatureTypeRecognizer.DateTime,
            should_output=True)
        # This transformation depends on the previous transformation
        datatime_string_cast_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=_TransformationFunctionNames.StringCast,
            operator=None, feature_type=None,
            should_output=False)
        # This transformation depends on the previous transformation
        datatime_datetime_transformer = _Transformer(
            parent_feature_list=[2],
            transformation_fnc=_TransformationFunctionNames.DateTime,
            operator=None, feature_type=None,
            should_output=False)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers(
            [datatime_imputer_transformer,
             datatime_string_cast_transformer,
             datatime_datetime_transformer])
        # Create the JSON object
        json_obj = \
            feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        alias_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

        # Add the transformations to be done and get the alias name
        # for the raw column.
        tr = [(column,
               [CatImputer(logger=self.logger),
                StringCastTransformer(logger=self.logger),
                DateTimeFeaturesTransformer(logger=self.logger)],
               {'alias': str(alias_column_name)})]

        return tr

    def _get_categorical_transforms(self, column,
                                    column_name,
                                    num_unique_categories):
        """
        Create a list of transforms for categorical data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :param num_unique_categories: Number of unique categories
        :return: Categorical transformations to use in a list.
        """
        if num_unique_categories <= 2:

            # Add the transformations to be done and get the alias name
            # for the hashing label encode transform.
            cat_two_category_imputer_transformer = _Transformer(
                parent_feature_list=[str(column_name)],
                transformation_fnc=_TransformationFunctionNames.Imputer,
                operator=_OperatorNames.Mode,
                feature_type=FeatureTypeRecognizer.Categorical,
                should_output=True)
            # This transformation depends on the previous transformation
            cat_two_category_string_cast_transformer = _Transformer(
                parent_feature_list=[1],
                transformation_fnc=_TransformationFunctionNames.StringCast,
                operator=None, feature_type=None,
                should_output=False)
            # This transformation depends on the previous transformation
            cat_two_category_label_encode_transformer = _Transformer(
                parent_feature_list=[2],
                transformation_fnc=_TransformationFunctionNames.LabelEncoder,
                operator=None, feature_type=None,
                should_output=True)
            # Create an object to convert transformations into JSON object
            feature_transformers = _FeatureTransformers(
                [cat_two_category_imputer_transformer,
                 cat_two_category_string_cast_transformer,
                 cat_two_category_label_encode_transformer])
            # Create the JSON object
            json_obj = \
                feature_transformers.encode_transformations_from_list()
            # Persist the JSON object for later use and obtain an alias name
            alias_column_name = \
                self._engineered_feature_names_class.\
                get_raw_feature_alias_name(json_obj)

            # Add the transformations to be done and get the alias name
            # for the raw column.
            tr = [(column,
                   [CatImputer(logger=self.logger),
                    StringCastTransformer(logger=self.logger),
                    LabelEncoderTransformer(
                        hashing_seed_val=self._hashing_seed_value,
                        logger=self.logger)],
                   {'alias': str(alias_column_name)})]

            return tr
        else:
            # Add the transformations to be done and get the alias name
            # for the hashing one hot encode transform.
            cat_multiple_category_string_cast_transformer = _Transformer(
                parent_feature_list=[str(column_name)],
                transformation_fnc=_TransformationFunctionNames.StringCast,
                operator=None, feature_type=FeatureTypeRecognizer.Categorical,
                should_output=False)
            # This transformation depends on the previous transformation
            cat_multiple_category_countvec_transformer = _Transformer(
                parent_feature_list=[1],
                transformation_fnc=_TransformationFunctionNames.CountVec,
                operator=_OperatorNames.CharGram, feature_type=None,
                should_output=True)
            # Create an object to convert transformations into JSON object
            feature_transformers = _FeatureTransformers([
                cat_multiple_category_string_cast_transformer,
                cat_multiple_category_countvec_transformer])
            # Create the JSON object
            json_obj = \
                feature_transformers.encode_transformations_from_list()
            # Persist the JSON object for later use and obtain an alias name
            alias_column_name = \
                self._engineered_feature_names_class.\
                get_raw_feature_alias_name(json_obj)

            # use CountVectorizer for both Hash and CategoricalHash for now
            tr = [(column, [StringCastTransformer(logger=self.logger),
                            CountVectorizer(
                                tokenizer=self._wrap_in_lst,
                                binary=True)
                            ],
                   {'alias': str(alias_column_name)})]

            return tr

    def _get_numeric_transforms(self, column, column_name):
        """
        Create a list of transforms for numerical data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :return: Numerical transformations to use in a list.
        """
        # Add the transformations to be done and get the alias name
        # for the numerical transform
        numeric_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.Imputer,
            operator=_OperatorNames.Mean,
            feature_type=FeatureTypeRecognizer.Numeric,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers([numeric_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        alias_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

        # Add the transformations to be done and get the alias name
        # for the imputation marker transform.
        # floats or ints go as they are, we only fix NaN
        tr = [([column], [Imputer()], {'alias': str(alias_column_name)})]

        return tr

    def _get_imputation_marker_transforms(self, column, column_name):
        """
        Create a list of transforms for numerical data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :return: Numerical transformations to use in a list.
        """
        # Add the transformations to be done and get the alias name
        # for the imputation marker transform.
        imputation_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.ImputationMarker,
            operator=None, feature_type=FeatureTypeRecognizer.Numeric,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers([imputation_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        alias_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

        # Add the transformations to be done and get the alias name
        # for the imputation marker transform.
        tr = [([column],
               [ImputationMarker(logger=self.logger)],
               {'alias': str(alias_column_name)})]

        return tr

    def _get_text_transforms(self, column, column_name, ngram_len):
        """
        Create a list of transforms for text data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :param ngram_len: Continous length of characters or number of words.
        :return: Text transformations to use in a list.
        """
        ngram_len = min(self._max_ngram, ngram_len)

        # Add the transformations to be done and get the alias name
        # for the trichar transform.
        text_trichar_string_cast_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.StringCast,
            operator=None, feature_type=FeatureTypeRecognizer.Text,
            should_output=False)
        # This transformation depends on the previous transformation
        text_trichar_tfidf_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=_TransformationFunctionNames.Tf,
            operator=_OperatorNames.CharGram, feature_type=None,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers([
            text_trichar_string_cast_transformer,
            text_trichar_tfidf_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        tfidf_trichar_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)

        # Add the transformations to be done and get the alias name
        # for the bigram word transform.
        text_biword_string_cast_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.StringCast,
            operator=None, feature_type=FeatureTypeRecognizer.Text,
            should_output=False)
        # This transformation depends on the previous transformation
        text_biword_tfidf_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=_TransformationFunctionNames.Tf,
            operator=_OperatorNames.WordGram, feature_type=None,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers([
            text_biword_string_cast_transformer,
            text_biword_tfidf_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        tfidf_biword_column_name = \
            self._engineered_feature_names_class.get_raw_feature_alias_name(
                json_obj)
        tr = [(column,
               [
                   StringCastTransformer(logger=self.logger),
                   TfidfVectorizer(use_idf=False, norm='l2', max_df=0.95,
                                   analyzer='char',
                                   ngram_range=(1, ngram_len))
               ],
               {
                   'alias': str(tfidf_trichar_column_name)
               }
               ),
              (column,
               [
                   StringCastTransformer(logger=self.logger),
                   TfidfVectorizer(use_idf=False, norm='l2',
                                   analyzer='word',
                                   ngram_range=(1, 2))
               ],
               {
                   'alias': str(tfidf_biword_column_name)
               }
               )]

        if self._task_type == constants.Tasks.CLASSIFICATION:
            # Add the transformations to be done and get the alias name
            # for the count vec transform.
            text_imputer_transformer = _Transformer(
                parent_feature_list=[str(column_name)],
                transformation_fnc=_TransformationFunctionNames.Imputer,
                operator=_OperatorNames.Mode,
                feature_type=FeatureTypeRecognizer.Text,
                should_output=True)
            # This transformation depends on the previous transformation
            text_string_cast_transformer = _Transformer(
                parent_feature_list=[1],
                transformation_fnc=_TransformationFunctionNames.StringCast,
                operator=None, feature_type=None,
                should_output=False)
            # This transformation depends on the previous transformation
            text_countvec_transformer = _Transformer(
                parent_feature_list=[2],
                transformation_fnc=_TransformationFunctionNames.CountVec,
                operator=_OperatorNames.WordGram, feature_type=None,
                should_output=True)
            # This transformation depends on the previous transformation
            text_naivebayes_transformer = _Transformer(
                parent_feature_list=[3],
                transformation_fnc=_TransformationFunctionNames.NaiveBayes,
                operator=None, feature_type=None,
                should_output=True)
            # Create an object to convert transformations into JSON object
            feature_transformers = _FeatureTransformers([
                text_imputer_transformer,
                text_string_cast_transformer,
                text_countvec_transformer,
                text_naivebayes_transformer])
            # Create the JSON object
            json_obj = feature_transformers.encode_transformations_from_list()
            # Persist the JSON object for later use and obtain an alias name
            count_vec_column_name = \
                self._engineered_feature_names_class.\
                get_raw_feature_alias_name(json_obj)

            # Add the transformations to be done and get the alias name
            # for the raw column.
            tr.append((column,
                       [
                           CatImputer(logger=self.logger),
                           StringCastTransformer(logger=self.logger),
                           CountVectorizer(analyzer='word',
                                           ngram_range=(1, 1)),
                           NaiveBayes(logger=self.logger)
                       ],
                       {
                           'alias': str(count_vec_column_name)
                       }))

        return tr

    def _wrap_in_lst(self, x):
        """
        Wrap an element in list.

        :param x: Element like string or integer.
        """
        return [x]

    def _get_transformations_str(self, df, transforms):
        """
        Get the data transformations recorded for raw columns as strings.

        :param df: Input dataframe.
        :type df:numpy.ndarray or pandas.DataFrame or sparse matrix
        :param transforms: List of applied transformations for various raw
        columns as a string.
        :type transforms: List
        """
        transformation_str = 'Transforms:\n'
        list_of_transforms_as_list = []

        # Walk all columns in the input dataframe
        for column in df.columns:

            # Get all the indexes of transformations for the current column
            column_matches_transforms = \
                [i for i in range(0, len(transforms))
                 if transforms[i][0] == column]

            # If no matches for column name is found, then look for list having
            # this column name
            if len(column_matches_transforms) == 0:
                column_matches_transforms = \
                    [i for i in range(0, len(transforms))
                     if transforms[i][0] == [column]]

            # Walk all the transformations found for the current column and add
            # to a string
            for transform_index in column_matches_transforms:
                some_str = 'col {}, transformers: {}'.format(
                    df.columns.get_loc(column),
                    '\t'.join([tf.__class__.__name__ for tf
                               in transforms[transform_index][1]]))
                list_of_transforms_as_list.append(some_str)

        transformation_str += '\n'.join(list_of_transforms_as_list)

        # Return the string representation of all the transformations
        return transformation_str


class LaggingTransformer(BaseEstimator, TransformerMixin, TransformerLogger):
    """
    Transforms the input data by appending previous rows.

    :param lag_length: Lagging length.
    :type lag_length: int
    """

    def __init__(self, lag_length, logger=None):
        """
        Initialize for lagging transform with lagging length.

        :param lag_length: Lagging length.
        :type lag_length: int
        :return:
        """
        self._lag_length = lag_length
        self._missing_fill = 0
        self._init_logger(logger)
        self._engineered_feature_names = []
        self._are_engineered_feature_names_available = False

    def _learn_transformations(self, x, y=None):
        """
        Learn data transformation to be done on the raw data.

        :param x: Input dataframe or sparse matrix.
        :type x: numpy.ndarray or pandas.DataFrame or sparse matrix
        :param y: Target values.
        :type y: numpy.ndarray or pandas.DataFrame
        """
        pass

    def fit(self, x, y=None):
        """
        Fit function for lagging transform.

        :param x: Input dataframe or sparse matrix.
        :type x: numpy.ndarray or pandas.DataFrame or sparse matrix
        :param y: Target values.
        :type y: numpy.ndarray or pandas.DataFrame
        :return: Class object itself.
        """
        self._learn_transformations(x, y)
        if not self._are_engineered_feature_names_available:
            # Generate engineered feature names
            self._generate_engineered_feature_names(x)

            self._are_engineered_feature_names_available = True

        return self

    def get_engineered_feature_names(self):
        """
        Return the list of engineered feature names as string.

        Return the list of engineered feature names as string after data transformations
        on the raw data have been finished.

        :return: The list of engineered fearure names as strings
        """
        return self._engineered_feature_names

    def _generate_engineered_feature_names(self, x):
        """
        Generate engineered feature names for lagging transformer features.

        :type x: numpy.ndarray or pandas.DataFrame or sparse matrix
        :param y: Target values.
        """
        raw_feature_names = None
        if isinstance(x, pd.DataFrame) or isinstance(x, pd.SparseDataFrame):
            raw_feature_names = x.columns

        # If no raw feature names are available, prefix them with 'C'
        column_name = 'C'
        temp_list = []
        if raw_feature_names is None:
            if len(x.shape) == 1:
                num_cols = 1
            else:
                num_cols = x.shape[1]
            for index in range(1, num_cols + 1):
                temp_list.append(column_name + str(index))
        elif isinstance(raw_feature_names[0], (int, np.integer)):
            for index in range(1, len(raw_feature_names) + 1):
                temp_list.append(column_name + str(index))
        else:
            for index in range(len(raw_feature_names)):
                temp_list.append(raw_feature_names[index])

        # For each lag length generate the engineered feature name of the format
        # "raw_feature_name" + "_lag_" + str(lag_length).
        for lag_length in range(0 + self._lag_length + 1):
            for index, raw_feature_name in enumerate(temp_list):
                if lag_length == 0:
                    engineered_name = temp_list[index]
                else:
                    engineered_name = temp_list[index] + '_lag_' + str(lag_length)

                # Add the engineered name to the list
                self._engineered_feature_names.insert(index + lag_length * len(temp_list), engineered_name)

    @function_debug_log_wrapped
    def transform(self, x):
        """
        Transform function for lagging transform.

        The function appends columns with previous seen rows to the input dataframe
        or sparse matrix depending on the specified lagging length.

        :param x: Input dataframe or sparse matrix.
        :type x: numpy.ndarray or pandas.DataFrame or sparse matrix
        :return: Result of lagging transform.
        """
        # If we get a sparse data frame, convert to sparse matrix
        if isinstance(x, pd.SparseDataFrame):
            x = x.to_coo().tocsr()

        x_is_sparse = sparse.issparse(x)

        if not isinstance(x, pd.DataFrame) and not isinstance(x, np.ndarray) \
                and not x_is_sparse:
            raise ValueError(
                "x should be dataframe or numpy array or scipy sparse matrix")

        if x.shape[0] < self._lag_length:
            raise ValueError(
                "Input needs to have at least {0} rows"
                .format(self._lag_length))

        if isinstance(x, np.ndarray):
            df = pd.DataFrame(x)
        elif x_is_sparse:
            # SparseDataFrame throws error with to_coo if dtype is int
            df = pd.SparseDataFrame(x.astype(float))
        else:
            df = x

        df_lag = df
        for i in range(1, self._lag_length + 1):
            df_lag = pd.concat([df_lag, df.shift(i)], axis=1)

        df_lag.columns = self._engineered_feature_names
        return df_lag.to_coo().tocsr() if x_is_sparse else \
            df_lag.fillna(self._missing_fill).values
