import os
import pandas as pd
import numpy as np
import time
import pkg_resources
import math
import localpath

from datetime import timedelta

from ftk import ForecastDataFrame, MultiForecastDataFrame
from ftk.models import RegressionForecaster
from ftk.pipeline import AzureMLForecastPipeline
from ftk.operationalization import ScoreContext
from ftk.transforms import TimeSeriesImputer, TimeIndexFeaturizer, DropColumns
from ftk.transforms import GrainIndexFeaturizer
from sklearn.ensemble import RandomForestRegressor
from ftk.model_selection import TSGridSearchCV, RollingOriginValidator
from ftk import TimeSeriesDataFrame
from ftk.data import load_dominicks_oj_dataset

from ftk.testing.abstract_test_data_provider import AbstractTestDataProvider

class DominicksTestDataProvider(AbstractTestDataProvider):
    """.. py:class:: DominicksTestDataProvider
    The class to generate test and train data frames based on Dominicks orange juice data set. 
    """
    #The fitted pipeline.
    _pipeline = None
    
    def __init__(self):
        """Constructor.
        Load data.
        """
        self.train_ts, self.test_ts = load_dominicks_oj_dataset()
        self.df_test = self.test_ts._extract_time_series(colnames = list(self.test_ts.columns.values)).reset_index()
        self.df_test['WeekLastDay'] = pd.to_datetime(self.df_test['WeekLastDay'])

        # Use a TimeSeriesImputer to linearly interpolate missing values
        imputer = TimeSeriesImputer(input_column='Quantity', 
                                    option='interpolate',
                                    method='linear',
                                    freq='W-WED')
        
        self.train_imputed_tsdf = imputer.transform(self.train_ts)

        self.validate_ts = self.train_imputed_tsdf.assign(PointForecast=0.0, DistributionForecast=np.nan)
        validate_fcast = ForecastDataFrame(self.validate_ts, pred_point='PointForecast', pred_dist='DistributionForecast')
        
        test_ts = self.test_ts.assign(PointForecast=0.0, DistributionForecast=np.nan)
        self.test_fcast = ForecastDataFrame(test_ts, pred_point='PointForecast', pred_dist='DistributionForecast')
        test_multicast = self.test_fcast.assign(Model=np.zeros((len(self.test_fcast),)))
        self._mcast_df = MultiForecastDataFrame(data = test_multicast, model_colnames='Model')
        self.score_context_train_predict= ScoreContext(input_training_data_tsdf=self.train_ts,
                                                   input_scoring_data_fcdf=self.test_fcast, 
                                                   pipeline_execution_type='train_predict')
        
        self.score_context_train_only = ScoreContext(input_training_data_tsdf=self.train_ts,
                                                   pipeline_execution_type='train_only')
        
        self.score_context_predict_only = ScoreContext(input_scoring_data_fcdf=self.test_fcast, 
                                                   pipeline_execution_type='predict_only')
        # Define Score Context
        self.score_context_validate = ScoreContext(input_training_data_tsdf=self.train_imputed_tsdf,
                                                   input_scoring_data_fcdf=validate_fcast, 
                                                   pipeline_execution_type='train_predict')
        
    def get_pipeline(self):
        """.. py:method:: get_pipeline()
        Return the fitted pipeline for the given example data.
        The pipeline implementation is dependent on the exact data provider.
        :returns: the pipeline.
        :rtype: AzureMLForecastPipeline.
        """
        if not DominicksTestDataProvider._pipeline:
            oj_series_freq = 'W-WED'
            oj_series_seasonality = 52
            
            # DropColumns: Drop columns that should not be included for modeling. `logmove` is the log of the number of 
            # units sold, so providing this number would be cheating. `WeekFirstDay` would be 
            # redundant since we already have a feature for the last day of the week.
            columns_to_drop = ['logmove', 'WeekFirstDay', 'week']
            column_dropper = DropColumns(columns_to_drop)
            # TimeSeriesImputer: Fill missing values in the features
            # First, we need to create a dictionary with key as column names and value as values used to fill missing 
            # values for that column. We are going to use the mean to fill missing values for each column.
            columns_with_missing_values = self.train_imputed_tsdf.columns[pd.DataFrame(self.train_imputed_tsdf).isnull().any()].tolist()
            columns_with_missing_values = [c for c in columns_with_missing_values if c not in columns_to_drop]
            missing_value_imputation_dictionary = {}
            for c in columns_with_missing_values:
                missing_value_imputation_dictionary[c] = self.train_imputed_tsdf[c].mean()
            fillna_imputer = TimeSeriesImputer(option='fillna', 
                                               input_column=columns_with_missing_values,
                                               value=missing_value_imputation_dictionary)
            # TimeIndexFeaturizer: extract temporal features from timestamps
            time_index_featurizer = TimeIndexFeaturizer(correlation_cutoff=0.1, overwrite_columns=True, )
            
            # GrainIndexFeaturizer: create indicator variables for stores and brands
            grain_featurizer = GrainIndexFeaturizer(overwrite_columns=True, ts_frequency=oj_series_freq)
            
            random_forest_model_deploy = RegressionForecaster(estimator=RandomForestRegressor(), make_grain_features=False)
            
            DominicksTestDataProvider._pipeline = AzureMLForecastPipeline([('drop_columns', column_dropper), 
                                                       ('fillna_imputer', fillna_imputer),
                                                       ('time_index_featurizer', time_index_featurizer),
                                                       ('random_forest_estimator', random_forest_model_deploy)
                                                      ])
            DominicksTestDataProvider._pipeline.fit(self.train_imputed_tsdf)
        return DominicksTestDataProvider._pipeline