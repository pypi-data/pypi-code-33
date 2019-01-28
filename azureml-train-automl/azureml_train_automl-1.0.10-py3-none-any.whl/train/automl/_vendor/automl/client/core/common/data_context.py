# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holding the data context classes."""
import logging
import os

from . import constants
from .cache_store import CacheStore, MemoryCacheStore
from .utilities import _get_ts_params_dict


class BaseDataContext(object):
    """Base data context class for input raw data and output transformed data."""

    def __init__(self,
                 X,
                 y=None,
                 X_valid=None,
                 y_valid=None,
                 sample_weight=None,
                 sample_weight_valid=None,
                 x_raw_column_names=None,
                 cv_splits_indices=None,
                 num_cv_folds=None,
                 validation_size=None):
        """
        Construct the BaseDataContext class.

        :param X: Input training data.
        :type X: numpy.ndarray or pandas.DataFrame
        :param y: Input training labels.
        :type y: numpy.ndarray or pandas.DataFrame
        :param X_valid: validation data.
        :type X_valid: numpy.ndarray or pandas.DataFrame
        :param y_valid: validation labels.
        :type y_valid: numpy.ndarray or pandas.DataFrame
        :param sample_weight: Sample weights for training data.
        :type sample_weight: numpy.ndarray or pandas.DataFrame
        :param sample_weight_valid: validation set sample weights.
        :type sample_weight_valid: numpy.ndarray or pandas.DataFrame
        :params x_raw_column_names: raw feature names of X data.
        :type x_raw_column_names: numpy.ndarray
        :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
        :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
        :param num_cv_folds: Number of cross validation folds
        :type num_cv_folds: integer
        :param validation_size: Percentage of data to be held out for validation
        :type validation_size: Double
        """
        self.X = X
        self.y = y
        self.X_valid = X_valid
        self.y_valid = y_valid
        self.sample_weight = sample_weight
        self.sample_weight_valid = sample_weight_valid
        self.x_raw_column_names = x_raw_column_names
        self.cv_splits_indices = cv_splits_indices
        self.num_cv_folds = num_cv_folds
        self.validation_size = validation_size


class RawDataContext(BaseDataContext):
    """User provided data context."""

    def __init__(self,
                 task_type,
                 X,  # DataFlow or DataFrame
                 y=None,  # DataFlow or DataFrame
                 X_valid=None,  # DataFlow
                 y_valid=None,  # DataFlow
                 sample_weight=None,
                 sample_weight_valid=None,
                 preprocess=None,
                 lag_length=None,
                 x_raw_column_names=None,
                 cv_splits_indices=None,
                 num_cv_folds=None,
                 validation_size=None,
                 timeseries=False,
                 timeseries_param_dict=None,
                 automl_settings_obj=None):
        """
        Construct the RawDataContext class.

        :param X: Input training data.
        :type X: numpy.ndarray or pandas.DataFrame
        :param y: Input training labels.
        :type y: numpy.ndarray or pandas.DataFrame
        :param X_valid: validation data.
        :type X_valid: numpy.ndarray or pandas.DataFrame
        :param y_valid: validation labels.
        :type y_valid: numpy.ndarray or pandas.DataFrame
        :param sample_weight: Sample weights for training data.
        :type sample_weight: numpy.ndarray or pandas.DataFrame
        :param sample_weight_valid: validation set sample weights.
        :type sample_weight_valid: numpy.ndarray or pandas.DataFrame
        :param preprocess: The switch controls the preprocess.
        :type preprocess: bool
        :params x_raw_column_names: raw feature names of X data.
        :type x_raw_column_names: numpy.ndarray
        :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
        :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
        :param task_type: constants.Tasks.CLASSIFICATION or constants.Tasks.REGRESSION
        :type task_type: str
        :param num_cv_folds: Number of cross validation folds
        :type num_cv_folds: integer
        :param validation_size: Percentage of data to be held out for validation
        :type validation_size: Double
        :param automl_settings_obj: User settings specified when creating AutoMLConfig.
        :type automl_settings_obj: _AutoMLSettings
        """
        self.preprocess = preprocess
        self.lag_length = lag_length
        self.task_type = task_type
        self.timeseries = timeseries
        self.timeseries_param_dict = timeseries_param_dict

        if automl_settings_obj is not None:
            validation_size = automl_settings_obj.validation_size
            num_cv_folds = automl_settings_obj.n_cross_validations
            self.timeseries = automl_settings_obj.is_timeseries
            self.timeseries_param_dict = _get_ts_params_dict(automl_settings_obj)

        super().__init__(X=X, y=y,
                         X_valid=X_valid,
                         y_valid=y_valid,
                         sample_weight=sample_weight,
                         sample_weight_valid=sample_weight_valid,
                         x_raw_column_names=x_raw_column_names,
                         cv_splits_indices=cv_splits_indices,
                         num_cv_folds=num_cv_folds,
                         validation_size=validation_size)


class TransformedDataContext(BaseDataContext):
    """
    The user provided data with applied transformations.

    If there is no preprocessing this will be the same as the RawDataContext.
    This class will also hold the necessary transformers used.
    """

    FEATURIZED_CV_SPLIT_KEY_INITIALS = 'featurized_cv_split_'
    FEATURIZED_TRAIN_TEST_VALID_KEY_INITIALS = 'featurized_train_test_valid'

    def __init__(self,
                 X,  # DataFrame
                 y=None,  # DataFrame
                 X_valid=None,  # DataFrame
                 y_valid=None,  # DataFrame
                 sample_weight=None,
                 sample_weight_valid=None,
                 x_raw_column_names=None,
                 cv_splits_indices=None,
                 num_cv_folds=None,
                 validation_size=None,
                 cache_store=None,
                 logger=logging.getLogger(__name__)):
        """
        Construct the TransformerDataContext class.

        :param X: Input training data.
        :type X: numpy.ndarray or pandas.DataFrame
        :param y: Input training labels.
        :type y: numpy.ndarray or pandas.DataFrame
        :param X_valid: validation data.
        :type X_valid: numpy.ndarray or pandas.DataFrame
        :param y_valid: validation labels.
        :type y_valid: numpy.ndarray or pandas.DataFrame
        :param sample_weight: Sample weights for training data.
        :type sample_weight: numpy.ndarray or pandas.DataFrame
        :param sample_weight_valid: validation set sample weights.
        :type sample_weight_valid: numpy.ndarray or pandas.DataFrame
        :params x_raw_column_names: raw feature names of X data.
        :type x_raw_column_names: numpy.ndarray
        :param cv_splits_indices: Custom indices by which to split the data when running cross validation.
        :type cv_splits_indices: numpy.ndarray or pandas.DataFrame
        :param num_cv_folds: Number of cross validation folds
        :type num_cv_folds: integer
        :param validation_size: Fraction of data to be held out for validation
        :type validation_size: Float
        :param cache_store: cache store to use for caching transformed data. None means don't cache.
        :type cache_store: CacheStore
        :param logger: module logger
        :type logger: logger
        """
        super().__init__(X=X, y=y,
                         X_valid=X_valid,
                         y_valid=y_valid,
                         sample_weight=sample_weight,
                         sample_weight_valid=sample_weight_valid,
                         x_raw_column_names=x_raw_column_names,
                         cv_splits_indices=cv_splits_indices,
                         num_cv_folds=num_cv_folds,
                         validation_size=validation_size)
        self.cache_store = cache_store or MemoryCacheStore()
        self.module_logger = logger
        if self.module_logger is None:
            self.module_logger = logging.getLogger(__name__)
            self.module_logger.propagate = False

        self.transformers = dict()
        self._pickle_keys = ["X", "y", "X_valid", "y_valid", "sample_weight", "sample_weight_valid",
                             "x_raw_column_names", "cv_splits_indices", "run_id", "transformers",
                             "cv_splits", "_on_demand_pickle_keys"]
        self._on_demand_pickle_keys = []
        self._num_workers = os.cpu_count()
        self.transformers = dict()
        self.cv_splits = None

    def _set_transformer(self, x_transformer=None, lag_transformer=None, y_transformer=None, ts_transformer=None):
        """
        Set the x_transformer and lag_transformer.

        :param x_transformer: transformer for x transformation.
        :param lag_transformer: lag transformer.
        :param y_transformer: transformer for y transformation.
        :param ts_transformer: transformer for timeseries data transformation.
        """
        self.transformers[constants.Transformers.X_TRANSFORMER] = x_transformer
        self.transformers[constants.Transformers.LAG_TRANSFORMER] = lag_transformer
        self.transformers[constants.Transformers.Y_TRANSFORMER] = y_transformer
        self.transformers[constants.Transformers.TIMESERIES_TRANSFORMER] = ts_transformer

    def _get_engineered_feature_names(self):
        """Get the enigneered feature names available in different transformer."""
        if self.transformers[constants.Transformers.TIMESERIES_TRANSFORMER] is not None:
            return self.transformers[constants.Transformers.TIMESERIES_TRANSFORMER].get_engineered_feature_names()
        if self.transformers[constants.Transformers.LAG_TRANSFORMER] is not None:
            return self.transformers[constants.Transformers.LAG_TRANSFORMER].get_engineered_feature_names()
        elif self.transformers[constants.Transformers.X_TRANSFORMER] is not None:
            return self.transformers[constants.Transformers.X_TRANSFORMER].get_engineered_feature_names()
        else:
            return self.x_raw_column_names

    def _refit_transformers(self, X, y):
        """Refit raw training data on the data and lagging transformers."""
        if self.transformers[constants.Transformers.X_TRANSFORMER] is not None:
            self.transformers[constants.Transformers.X_TRANSFORMER].fit(X, y)

        if self.transformers[constants.Transformers.LAG_TRANSFORMER] is not None:
            self.transformers[constants.Transformers.LAG_TRANSFORMER].fit(X, y)

    def _load_from_cache(self):
        """Load data from cache store."""
        self.cache_store.load()
        retrieve_data_list = self.cache_store.get(self._pickle_keys)

        super().__init__(X=retrieve_data_list.get('X'), y=retrieve_data_list.get('y'),
                         X_valid=retrieve_data_list.get('X_valid'),
                         y_valid=retrieve_data_list.get('y_valid'),
                         sample_weight=retrieve_data_list.get('sample_weight'),
                         sample_weight_valid=retrieve_data_list.get('sample_weight_valid'),
                         x_raw_column_names=retrieve_data_list.get('x_raw_column_names'),
                         cv_splits_indices=retrieve_data_list.get('cv_splits_indices'))
        self.transformers = retrieve_data_list.get('transformers')
        self.cv_splits = retrieve_data_list.get('cv_splits')
        self._on_demand_pickle_keys = retrieve_data_list.get('_on_demand_pickle_keys')

        if self.module_logger:
            self.module_logger.info('The on-demand pickle keys are: ' + str(self._on_demand_pickle_keys))

    def _clear_cache(self):
        """Clear the in-memory cached data to lower the memory consumption."""
        self.X = None
        self.y = None
        self.X_valid = None
        self.y_valid = None
        self.sample_weight = None
        self.sample_weight_valid = None
        self.x_raw_column_names = None
        self.cv_splits_indices = None
        self.run_id = None
        self.transformers = None
        self.cv_splits = None
        self._on_demand_pickle_keys = None

    def _update_cache(self):
        """Update the cache based on run id."""
        for k in self._pickle_keys:
            self._add_to_cache(k)

    def _update_cache_with_featurized_data(self, featuruzed_data_key, featurized_data):
        """
        Update the cache with the featurized data.

        :param featuruzed_data_key: pickle key
        :param featurized_data: featurized data
        """
        self._on_demand_pickle_keys.append(featuruzed_data_key)

        self._add_to_cache(featuruzed_data_key, featurized_data)
        if self.module_logger:
            self.module_logger.info("Adding pickle key: " + featuruzed_data_key)

    def _add_to_cache(self, k, value=None):
        """
        Add the contents of transformed data to cache.

        :param k: pickle key
        :param value: data to be added to the cache
        """
        if k in self.__dict__:
            self.cache_store.add([k], [self.__dict__.get(k)])
        elif value is not None:
            self.cache_store.add([k], [value])

    def cleanup(self):
        """Clean up the cache."""
        try:
            # unload deletes the files
            self.cache_store.unload()
        except IOError as e:
            self.module_logger.warning("Failed to unload the cache store {}".format(e))
