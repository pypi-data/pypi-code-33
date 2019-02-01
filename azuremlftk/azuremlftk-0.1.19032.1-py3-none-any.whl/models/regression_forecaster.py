from warnings import warn, catch_warnings, simplefilter
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, RegressorMixin, MetaEstimatorMixin
from sklearn.base import clone as sklearn_estimator_clone
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from ftk import verify
from ftk.base_estimator import AzureMLForecastRegressorBase, loggable
from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.forecast_data_frame import ForecastDataFrame
from ftk.pipeline import AzureMLForecastPipeline
from ftk.models.sklearn_estimator_wrapper import SklearnEstimatorWrapper

from ftk.exception import (EstimatorTypeException, EstimatorValueException,
                           InvalidEstimatorTypeException, 
                           NotTimeSeriesDataFrameException,
                           DatetimeConversionException, DataFrameTypeException, 
                           DataFrameValueException)
from ftk.constants import *

# Subclassing regressor base for now, 
# but perhaps this should be a meta-estimator? 
class RegressionForecaster(AzureMLForecastRegressorBase):
    """
    This class enables regression learning on a TimeSeriesDataFrame
    with any sklearn regression estimator.

    RegressionForecaster learns a separate model for each group 
    in an input :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`.
    :func: `TimeSeriesDataFrame.group_colnames` determines the groups.

    .. _sklearn.base.BaseEstimator: http://scikit-learn.org/stable/modules/generated/sklearn.base.BaseEstimator.html
    .. _sklearn.base.RegressorMixin: http://scikit-learn.org/stable/modules/generated/sklearn.base.RegressorMixin.html
    .. _sklearn.base.MetaEstimatorMixin: http://scikit-learn.org/stable/modules/classes.html


    In order to get distribution forecasts from a RegressionForecaster, 
    the forecaster must be fit using a `TSGridSearchCV` search object 
    with a `RollingOriginValidator` validator object.  This is because 
    the results of the rolling origin cross-validation are used to 
    determine the empirical distribution of out of sample errors.
        
    :param estimator: Sklearn regression estimator 
    :type estimator: 
        sklearn.base.BaseEstimator_,
        sklearn.base.RegressorMixin_,
        sklearn.base.MetaEstimatorMixin_.

    :param internal_featurization:
        Allow the forecaster to create features internally
        prior to estimation.

        If set to True, a `BasicRegressionFeaturizerFactory`
        pipeline factory will be used to construct
        a featurization pipeline and this pipeline will be run prior 
        to fit/predict on internal models. 

        This option is not recommended when RegressionForecast.fit/predict
        will be called in a loop (i.e. during cross-validation)
        since it will re-featurize the data on every iteration.
        Use a separate featurization pipeline outside the loop in
        these cases.
    :type internal_featurization: boolean

    :param make_grain_features:
        Should the forecaster make grain and horizon features prior to
        estimation? If so, RegressionForecaster applies a 
        GrainIndexFeaturizer transform in fit/predict.
        Column names corresponding to these features will
        begin with 'grain' and 'horizon.'
        If these columns already exist in the dataframe,
        the fit method will overwrite them and print a 
        warning.

        This option is ignored if internal_featurization=False
    :type make_grain_features: boolean, default: True


    :param ts_frequency:
        The frequency of the time series being forecasted
        as an offset alias string or a DateOffset object.
        This parameter is used to construct the horizon feature.
        Ignored if `make_grain_features=False`.
        If `ts_frequency=None`, the fit method will attempt to infer 
        the frequency from the input TimeSeriesDataFrame.
    :type ts_frequency: 
        str, pandas.DateOffset

    :param one_model_per_horizon:
        If True, one model is trained for each group + horizon
        combination. Otherwise, one model is trained for each `group` by
        default.
    :type one_model_per_horizon: boolean

    """

    def __init__(self, estimator=LinearRegression(),
                 internal_featurization=True,
                 make_grain_features=True,
                 ts_frequency=None,
                 one_model_per_horizon=False):
        
        # Import pipeline factory here to avoid circular import of
        #  RegressionForecaster
        from ftk.pipeline_factories import BasicRegressionFeaturizerFactory
        self.estimator = estimator
        self.internal_featurization = internal_featurization
        self.make_grain_features = make_grain_features
        self.ts_frequency = ts_frequency
        self.one_model_per_horizon = one_model_per_horizon

        if not internal_featurization and make_grain_features:
            warn('RegressionForecaster: incompatible settings ' +
                 'internal_featurization=False and make_grain_features=True. ' +
                 'Setting make_grain_features=False', UserWarning)
            self.make_grain_features = False

        self._featurization_factory = \
            BasicRegressionFeaturizerFactory(time_index_features=False,
                                             grain_index_features=True,
                                             horizon_feature=True,
                                             binary_encode=True)
        self._featurizer_pipeline = None
        self._models = dict()
        self._write_origin_time = False
        self._origin_time_colname = None
        self._fcast_origin_dates = dict()
        self._is_fit = False
        self._input_features = list()
        self._features_in_fit = list()
        self._categorical_features = list()

    @property
    def estimator(self):
        """
        Internal sklearn estimator
        """
        return self._estimator

    @estimator.setter
    def estimator(self, val):
        # val should be an sklearn estimator
        #  and either be a regressor or a meta-estimator
        #  (e.g. a cross-validator)
        if isinstance(val, BaseEstimator) \
            and (isinstance(val, RegressorMixin) \
                 or isinstance(val, MetaEstimatorMixin)):
            self._estimator = val
        else:
            raise InvalidEstimatorTypeException(
                'estimator must be an sklearn regression estimator ' +
                'or a meta-estimator.')

    @property
    def one_model_per_horizon(self):
        return self._one_model_per_horizon

    @one_model_per_horizon.setter
    def one_model_per_horizon(self, val):
        if isinstance(val, bool):
           self._one_model_per_horizon = val
        else:
            raise ValueError('The "one_model_per_horizon" argument expects a '
                             'boolean value, {0} is passed instead.'
                             .format(type(val)))

    @property
    def features_in_fit(self):
        """
        Column names of the design matrices from a regression fit.
        """
        return self._features_in_fit if self._is_fit else None

    @property
    def is_fit(self):
        """
        Read-only boolean property indicating if the RegressionForecaster 
        object has been fit.
        """
        return self._is_fit

    def _prepare_feature_colnames(self, X, feature_colnames):

        # First, check and normalize the feature_colnames input
        # Should be a list of strings with no dups 
        if verify.is_iterable_but_not_string(feature_colnames):
            if all(isinstance(f, str) for f in feature_colnames):
                # Cast to set to remove duplicates
                feature_colnames = list(set(feature_colnames))
            else:
                raise EstimatorTypeException(
                    'features column names must all be strings.')

        elif isinstance(feature_colnames, str):
            feature_colnames = [feature_colnames]

        elif feature_colnames is None:
            pass

        else:
            raise EstimatorTypeException(
                'features column names can be None, a string, ' +
                'or an iterable containing strings')

        # Second, check feature_colnames against the data frame, X
        
        # If feature_colnames is None/empty use all X columns
        #   except target and time column
        forbidden_feats = [X.ts_value_colname, X.time_colname]
        final_features = feature_colnames
        if final_features is None or len(final_features) == 0:
            final_features = [col for col in X.columns 
                              if col not in forbidden_feats]
        
        # Check if target is in feature list
        # If so, print a warning and remove it 
        if X.ts_value_colname in final_features:
            warn('Target {0} is in the feature list. Removing it.'.format(
                X.ts_value_colname),
                 UserWarning)
            final_features.remove(X.ts_value_colname)

        # Check if some features are not in X
        # If so, remove them and print a warning
        not_in_frame = set(final_features) - set(X.columns)
        if len(not_in_frame) > 0:
            warn(('feature columns {0} are not present in the DataFrame. ' +
                  'Removing them').format(not_in_frame),
                 UserWarning)

            final_features = [col for col in final_features
                              if col not in not_in_frame]

        # Make sure there are some features left
        if len(final_features) == 0:
            raise EstimatorValueException('feature list is empty.')

        return final_features

    def preview_prediction_colnames(self, X):
        """
        Preview the names of point and distribution forecast columns
        that would be created/filled in X.

        :param X: Input data frame
        :type X: TimeSeriesDataFrame, ForecastDataFrame

        :return: Point and distribution forecast column names
        :rtype: tuple
        """
        pred_point_colname = None
        pred_dist_colname = None
        if isinstance(X, ForecastDataFrame):
            if X.pred_point is not None:
                pred_point_colname = X.pred_point
            if X.pred_dist is not None:
                pred_dist_colname = X.pred_dist

        if pred_point_colname is None:
            pred_point_colname = UNIFORM_PRED_POINT_COLNAME
        if pred_dist_colname is None:
            pred_dist_colname = UNIFORM_PRED_DIST_COLNAME

        return pred_point_colname, pred_dist_colname

    @loggable
    def fit(self, X, y=None, feature_colnames=None, 
            categorical_features=None, **fit_params):
        """
        Fit models on each group in X

        :param X: Training data
        :type X: TimeSeriesDataFrame
        :param y: 
            Target quantity. Ignored since X contains 
            the target quantity
        :param feature_colnames: 
            Column names of features to use in the regressions. 
            If feature_colnames is None, all columns 
            except ts_value will be used as features.
        :type feature_colnames: iterable of str
        :param categorical_features: 
            Column names of categorical features.
            These features will be dummy coded prior to
            estimation.
            If categorical_features is None, all columns 
            with dtype=object or dtype=category
            are considered categorical
        :type categorical_features: iterable of str
        :param fit_params: 
            Additional parameters to pass to the estimator's
            fit method
        :type fit_params: dict

        :returns: fit model
        :rtype: RegressionForecaster
        :raises: 
            NotTimeSeriesDataFrameException, EstimatorValueException,
            EstimatorTypeException 
        """

        # Make sure X is a TimeSeriesDataFrame
        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                'RegressionForecast.fit expects a TimeSeriesDataFrame')

        # Check if y input is set
        # If so, alert user that it is currently ignored
        if y is not None:
            warn('y input currently ignored. ' +
                 'X.ts_value used as the target quantity by default.',
                 UserWarning)

        feature_cols = self._prepare_feature_colnames(X, feature_colnames)
        X_cat_cols = X.select_dtypes(include=['object', 'category']).columns
        present_categoricals = [col for col in feature_cols
                                if col in X_cat_cols]
        if not self.internal_featurization and len(present_categoricals) > 0:
            warn(('RegressionForecaster.fit: Input data frame has categorical ' +
                  'features, but internal featurization is turned off. ' +
                  'scikit-learn may not be able to fit the requested model. ' +
                  'Detected categoricals: {0}').format(present_categoricals),
                 UserWarning)

        # If internal featurization is on, construct the featurization pipeline
        #   and run it
        feats_and_target = feature_cols + [X.ts_value_colname]
        if self.internal_featurization:
            self._featurization_factory.categorical_features = \
                categorical_features
            self._featurization_factory.grain_index_features = \
                self.make_grain_features
            self._featurizer_pipeline = \
                self._featurization_factory.build(X)

            self._featurizer_pipeline._logging_on = False
            Xt = self._featurizer_pipeline.fit_transform(X[feats_and_target])
        else:
            Xt = X[feats_and_target]
        
        if self.one_model_per_horizon:
            X_grouped = Xt.groupby_group_and_horizon()
        else:
            X_grouped = Xt.groupby_group()

        cols_no_target = [col for col in Xt.columns
                          if col != X.ts_value_colname]
        # Internal fit for single group
        # ------------------------------------------------------------------
        def fit_one_group(X_gr):

            # First clone the estimator to propagate params
            est = sklearn_estimator_clone(self._estimator)

            # Wrap the estimator so that fit/predict can
            #  be called with TimeSeriesDataFrame input
            est_wrapper = SklearnEstimatorWrapper(est)
            
            return est_wrapper.fit(X_gr[cols_no_target],
                                   y=X_gr[X_gr.ts_value_colname],
                                   **fit_params)
        # ------------------------------------------------------------------

        self._models = {group_level: fit_one_group(X_gr) 
                        for group_level, X_gr in X_grouped}

        # Store the forecast origin dates for each group
        self._fcast_origin_dates = {group_level: X_gr.time_index.max()
                                    for group_level, X_gr in X_grouped}

        self._is_fit = True
        self._features_in_fit = cols_no_target
        self._input_features = feature_cols

        return self
        
    @loggable
    def predict(self, X):
        """
        Predict the target quantity for each group in X.
        If X is a TimeSeriesDataFrame, prediction columns
        with default names will be created in the output.

        :param X: Data to use for predict
        :type X: 
            :class:`ftk.forecast_data_frame.ForecastDataFrame`, 
            :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :return: Data with predictions
        :rtype: :class:`ftk.dataframe_forecast.ForecastDataFrame`
        :raises: EstimatorValueException, NotTimeSeriesDataFrameException

        """
       
        if not self._is_fit:
            raise EstimatorValueException(
                'RegressionForecaster.predict: fit must be called before '
                + 'predict.')
        
        if not isinstance(X, TimeSeriesDataFrame):
            # Invalid type - raise exception
            raise NotTimeSeriesDataFrameException(
                'RegressionForecaster.predict expects '
                + 'an instance of TimeSeriesDataFrame')

        pred_point_col, pred_dist_col = self.preview_prediction_colnames(X)

        # Create/overwrite forecast origin time column
        if X.origin_time_colname is None:
            self._write_origin_time = True
            self._origin_time_colname = ORIGIN_TIME_COLNAME_DEFAULT
            if self._origin_time_colname in X.columns:
                warn(('Column {0} already exists in the input data ' +
                      'and it will be overwritten to store ' +
                      'date at which forecast was made.').format(
                          self._origin_time_colname), UserWarning)

        # Run the internal featurization pipeline (if applicable)
        feature_cols = self._input_features
        if self.internal_featurization:
            Xt = self._featurizer_pipeline.transform(X[feature_cols])
        else:
            Xt = X[feature_cols]

        
        # Internal prediction function for single group
        # ------------------------------------------------------------------
        def predict_one_group(group_level, Xgr):

            # If there's no model for this group, return an empty frame
            if group_level not in self._models:
                warn((type(self).__name__ + '.predict: ' 
                     + 'No model found for group {0}')
                     .format(group_level), UserWarning)
                
                return pd.DataFrame()

            # Call the model predict method
            mod = self._models[group_level]
            fcast_origin_date = self._fcast_origin_dates[group_level]
            point_predictions = mod.predict(Xgr)

            # assign to data frame prediction columns
            assign_dict = {pred_point_col: point_predictions,
                           pred_dist_col: None}
            if self._write_origin_time:
                assign_dict.update({self._origin_time_colname: 
                                    fcast_origin_date})

            return pd.DataFrame(assign_dict, index=Xgr.index)
        # ------------------------------------------------------------------

        # Make a prediction for each group level
        # Combine back into a single ForecastDataFrame
        if self.one_model_per_horizon:
            X_grouped = Xt.groupby_group_and_horizon()
        else:
            X_grouped = Xt.groupby_group()

        X_predict_df = X_grouped.apply(lambda Xgr: 
                                       predict_one_group(Xgr.name, Xgr))


        # Join the prediction frame back with the input frame.
        # First create a plain data frame of the input 
        #   without the pred columns - we will get filled predictions 
        #   via the join.
        X_df = (pd.DataFrame(X, copy=False)
                .drop([pred_point_col, pred_dist_col], 
                      axis=1, errors='ignore'))
        
        if X_predict_df.empty:
            # If there are no trained models for any groups in X,
            #  X_predict_df will be an empty data frame
            
            empty_assign = {pred_point_col: np.nan, pred_dist_col: None}
            if self._write_origin_time:
                empty_assign[self._origin_time_colname] = pd.NaT 
                                  
            X_result_df = X_df.assign(**empty_assign)
        else:
            X_result_df = X_df.merge(X_predict_df, 
                                     right_index=True, left_index=True)
        ctr_args = {k: getattr(X, k) for k in X._metadata}
        if self._write_origin_time:
            ctr_args['origin_time_colname'] = self._origin_time_colname
        if not isinstance(X, ForecastDataFrame):
           
            X_result_tsdf = \
                TimeSeriesDataFrame(X_result_df, copy=False, **ctr_args) 
            X_result_fcdf = \
                ForecastDataFrame(X_result_tsdf, copy=False,
                                  pred_point=pred_point_col,
                                  pred_dist=pred_dist_col)
        else:
            X_result_fcdf = ForecastDataFrame(X_result_df, copy=False, 
                                              **ctr_args)

        with catch_warnings():
            simplefilter('ignore')
            X_result_fcdf._model_class_ = type(self._estimator).__name__
            X_result_fcdf._model_params_ = self._estimator.get_params()

        return X_result_fcdf

    def score(self, X, y=None):
        """
        Score function.
        Returns an average over the coefficients of determination
        for each group in X

        :param X: Input data to score
        :type X: TimeSeriesDataFrame
        """
        
        X_fcst = self.predict(X)

        if self.one_model_per_horizon:
            X_fcst_grouped = X_fcst.groupby_group_and_horizon()
        else:
            X_fcst_grouped = X_fcst.groupby_group()
       
        r2_scores = [r2_score(X_gr[X_fcst.actual].values, 
                              X_gr[X_fcst.pred_point].values)
                     for lvl, X_gr in X_fcst_grouped]

        return np.mean(r2_scores)

