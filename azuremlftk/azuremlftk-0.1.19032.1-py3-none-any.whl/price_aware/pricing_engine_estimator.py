from warnings import warn

import pandas as pd
import numpy as np
import scipy.stats

from ftk.base_estimator import AzureMLForecastRegressorBase
from ftk import TimeSeriesDataFrame, ForecastDataFrame
from ftk.constants import *

from pricingengine.schema import DataType, ColDef, Schema
from pricingengine.estimation.typed_dataset import ColType
from pricingengine.models.model import Model
from pricingengine.models.ols import OLS
from pricingengine.models.lasso import LassoCV
from pricingengine.estimation.estimation_dataset import EstimationDataSet
from pricingengine.estimation.dynamic_dml import DynamicDML, DDMLOptions
from pricingengine.featurizers.default_panel_featurizer import get_featurizer as get_panel_featurizer
from pricingengine.variables.own_var import OwnVar
from pricingengine.variables.p_to_p_var import PToPVar
from pricingengine.utilities.predictions import Predictions

from sklearn.model_selection import StratifiedKFold, GroupKFold, KFold
#Correct for the issue https://github.com/statsmodels/statsmodels/issues/4772
#AttributeError: 'function' object has no attribute 'im_self'
import ftk.price_aware.statsmodels_compat

class PricingEngineEstimator(AzureMLForecastRegressorBase):
    """
    Thin wrapper around pricingengine DynamicDML object (Double ML estimator)

    :param double_ml_estimator: 
        Pre-constructed pricingengine estimator object for double ML.
        If `None`, the fit method will create a default estimator object.
        See `PricingEngineEstimator.pricingengine_dml_helper`.
    :type double_ml_estimator: pricingengine.estimation.dynamic_dml.DynamicDML
    """

    def __init__(self, double_ml_estimator=None):
        
        self.double_ml_estimator = double_ml_estimator

    @property
    def double_ml_estimator(self):
        """
        Internal pricingengine estimator object (of type DynamicDML).
        See pricingengine documentation for the DynamicDML public interface.
        """
        return self._double_ml_estimator

    @double_ml_estimator.setter
    def double_ml_estimator(self, val):

        if val is not None and not isinstance(val, DynamicDML):
                raise TypeError('Value must be of type DynamicDML')

        self._double_ml_estimator = val

    @staticmethod
    def make_pricingengine_schema(X, treatment_colnames):
        """
        Make a pricingengine Schema object from a TimeSeriesDataFrame
        and a list of treatment column names in the data frame.

        The created Schema will classify all columns as either
        numeric, categorical, or date-time and identify
        outcome and treatment columns.

        :param X: Source Data Frame
        :type X: TimeSeriesDataFrame

        :param treatment_colnames: Columns in X to identify as treatments
        :type treatment_colnames: list of str

        :return: Schema object
        :rtype: pricingengine.schema.Schema
        """
        if isinstance(treatment_colnames, str):
            treatment_colnames = [treatment_colnames]
        elif isinstance(treatment_colnames, list):
            pass
        else:
            raise TypeError('treatment_colnames must be str or list. ' 
                            + 'Got type ' + type(treatment_colnames))

        outcome_col = set([X.ts_value_colname])
        cat_types = ['object', 'category']
        cat_columns = set(X.select_dtypes(include=cat_types).columns)
        num_columns = set(X.select_dtypes(include=['number']).columns)

        # To-do:
        # Figure out how to deal with "pre-determined" columns
        # i.e. features with values that are known contemporaneously 
        # at score time

        # Add grain columns to the list of categoricals
        cat_columns.update(X.grain_colnames)

        def make_coldef(colname):
            # Set the data type
            # The default condition will likely cause a downstream error 
            #  when the pricingengine validates the schema
            if colname in num_columns:
                data_type = DataType.NUMERIC
            elif colname in cat_columns:
                data_type = DataType.CATEGORICAL
            elif colname == X.time_colname:
                data_type = DataType.DATE_TIME
            else:
                data_type = None

            # Set the column type
            # Generally none, except for outcome and treatment columns
            if colname == X.ts_value_colname:
                col_type = ColType.OUTCOME
            elif colname in treatment_colnames:
                col_type = ColType.TREATMENT
            else:
                col_type = None

            return ColDef(colname, data_type, col_type)
        
        col_list = list(cat_columns) + list(num_columns) + [X.time_colname]
        coldef_list = [make_coldef(col) for col in col_list]

        return Schema(coldef_list, 
                      time_colname=X.time_colname, 
                      panel_colnames=X.grain_colnames)

    @staticmethod
    def make_pricingengine_dataset(X, schema):
        """
        Make a pricingengine EstimationDataset object
        from a TimeSeriesDataFrame and a Schema object.

        The returned dataset can be used in the pricingengine
        double-ML estimation methods.

        :param X: Source data frame
        :type X: TimeSeriesDataFrame

        :param schema: 
            Schema object for X. See `make_pricingengine_schema`.
        :type schema: pricingengine.schema.Schema

        :return: pricingengine representation of input data frame
        :rtype: pricingengine.estimation.estimation_dataset.EstimationDataSet
        """

        # Make a "flat" version of X by moving the time and grain
        #  indices into regular data frame columns
        col_list = schema.get_col_names()
        move_list = X.grain_colnames + [X.time_colname]
        X_flat = (pd.DataFrame(X)
                  .reset_index(level=move_list)
                  .reset_index(drop=True))[col_list]

        # *** 
        # This conversion may fail for TSDFs with origin times and other
        # index columns besides time and grain.
        # pricingengine expects that (time, grain) will be a unique row index.
        # Should probably add a validity check at the top of this utility
        # *** 

        return EstimationDataSet(X_flat, schema)

    @staticmethod
    def make_tsdf_from_pricingengine_dataset(X_pe):
        """
        Create a TimeSeriesDataFrame from a pricingengine
        EstimationDataset object.

        :param X_pe: pricingengine dataset
        :type X_pe: pricingengine.estimation.estimation_dataset.EstimationDataset

        :return: TimeSeriesDataFrame representation of the input dataset
        :rtype: TimeSeriesDataFrame
        """

        time_colname = X_pe.schema.get_time_col_name()
        grain_colnames = X_pe.schema.get_panel_col_names()

        return TimeSeriesDataFrame(X_pe.data, 
                                   time_colname=time_colname,
                                   grain_colnames=grain_colnames)
    
    @staticmethod
    def pricingengine_dml_helper(schema, min_lead=1, max_lead=1,
                                 baseline_model=LassoCV(), 
                                 causal_model=OLS(), 
                                 make_grain_features=True,
                                 make_time_dummies=False,
                                 causal_interaction_levels=None,
                                 sample_splitter=KFold(n_splits=3, 
                                                       shuffle=True)):
        """
        Helper utility for creating a priginegine DynamicDML object for
        double ML estimation. The DynamicDML objects this utility can
        create are limited to those with simple baseline (first stage) features 
        and self-elasticities in the causal (final stage) features.
        If a more complex model is needed (e.g. one that considers cross-price
        effects like cannibalization and substitution), then use the
        plain pricingengine DynamicDML constructor.

        The only mandatory parameter for the method is a pricingengine
        schema describing train/test datasets. All other parameters
        have simple defaults set.

        Note that the pricingengine creates separate, direct models for each
        lead/forecast horizon. The `min_lead` and `max_lead` parameters should
        be set according to the desired forecast horizon.

        :param min_lead: Minimum lead value for the model
        :type min_lead: int

        :param max_lead: 
            Maximum lead value for the model. Coincides with the maximum 
            desired forecast horizon
        :type max_lead: int

        :param baseline_model: 
            Model class to use for first stage (ML) regressions
        :type baseline_model: pricingengine.models.model.Model

        :param causal_model: 
            Model class to use for final stage (econometric) regression
        :type causal_model: pricingengine.models.model.Model

        :param make_grain_features:
            Whether to make categorical features for the time series
            grain ("panel variables" in the pricingengine)
            in the first stage regression
        :type make_grain_features: bool

        :param make_time_dummies:
            Whether to make categorical features for the time series
            time index in the first stage regression.
            This option should generally be `False` if the model will
            be asked to forecast values at date/times that are not
            present in training data.
        :type make_time_dummies: bool

        :param causal_interaction_levels:
            Categorical variables to interact with a treatment 
            in the final stage regression. 
            This determines the granularity of the inferred elasticity matrix.
            If `None`, no interaction features will be constructed.

            For example, if the dataset contains a treatment, 'logprice', and 
            a 'brand' column, then setting 
            `causal_interaction_levels={'logprice': [['brand']]}`
            will result in different elasticity estimates for each
            distinct brand.
        :type causal_interaction_levels: dict. str -> list of list

        :sample_splitter: 
            Sample splitter to use when training the first stage regressions.
            Internally, the pricingengine uses an ensemble method called 
            "cross-fitting" to reduce the effects of ML bias. This
            sample splitter will be used as part of training that ensemble.
            See the pricingengine documentation for more details.
        :type sample_splitter: sklearn.model_selection.BaseCrossValidator
        """
        
        options = DDMLOptions(min_lead, max_lead)
        baseline_builders = \
            get_panel_featurizer(schema, 
                                 panel_var_dummies=make_grain_features,
                                 time_dummies=make_time_dummies)

        # Make 2nd stage "self-elasticity" features.
        # Need a better way to create more complicated 2nd stage features
        # How do we indicate which peer-to-peer effects we want to model?
        treatment_cols = schema.get_colnames_bycoltype(ColType.TREATMENT)
        if causal_interaction_levels is None:
            causal_builders = \
                [OwnVar(col) for col in treatment_cols]
        else:
            causal_builders = \
                [OwnVar(col, 
                        interaction_levels=causal_interaction_levels[col]) 
                 for col in treatment_cols]

        return DynamicDML(schema, 
                          options=options,
                          baseline_model=baseline_model,
                          causal_model=causal_model,
                          feature_builders=baseline_builders,
                          treatment_builders=causal_builders,
                          sample_splitter=sample_splitter)

    def _pricingengine_predictions_to_fdf(self, tsdf_in, pe_predictions):
        """
        Private method for reshaping a pricingengine Predictions
        object into a ForecastDataFrame
        """

        # Filter down to just the dates passed in via X
        pred_dates = pe_predictions.index.get_level_values(tsdf_in.time_colname)
        df = pe_predictions[pred_dates.isin(tsdf_in.time_index)]
        
        pred_point_colname = 'PointForecast' + type(self).__name__
        pred_dist_colname = 'DistributionForecast' + type(self).__name__
        origin_colname = ORIGIN_TIME_COLNAME_DEFAULT
        ts_value_colname = tsdf_in.ts_value_colname
        time_colname = tsdf_in.time_colname

        lead_idx = df.columns.get_level_values(DynamicDML.LEAD_LEVEL_NAME)
        time_idx = df.index.get_level_values(time_colname)
        leads_present = lead_idx.unique()
        
        pe_pred_colname = Model.PREDICTION_COL_NAME
        pe_err_colname = Model.AVG_ERROR_COL_NAME
        pe_actual_colname = Predictions.ACTUAL_COL

        # If lead-0 is present, get the 'actuals'
        if 0 in leads_present:
            actuals = df[0][pe_actual_colname].values
        else:
            actuals = None

        # Extract the forecasts for a single lead
        # ---------------------------------------------------------
        def make_fcast_one_lead(lead):
            
            point_preds = df[lead][pe_pred_colname].values
            err_preds = df[lead][pe_err_colname].values
            dist_preds = [scipy.stats.norm(loc=pt,
                                           scale=err)
                          for pt, err in zip(point_preds, err_preds)]
            
            origin_dates = time_idx - lead * self._training_freq
            
            df_lead_dict = {pred_point_colname: point_preds,
                            pred_dist_colname: dist_preds,
                            origin_colname: origin_dates}
            if actuals is not None:
                df_lead_dict.update({ts_value_colname: actuals})
            return pd.DataFrame(df_lead_dict, index=df.index)
        # ---------------------------------------------------------

        fcast_df = pd.concat([make_fcast_one_lead(lead)
                              for lead in leads_present
                              if lead > 0])

        actual_colname = ts_value_colname if actuals is not None else None
        return ForecastDataFrame(fcast_df, time_colname=time_colname,
                                 grain_colnames=tsdf_in.grain_colnames,
                                 origin_time_colname=origin_colname,
                                 pred_point=pred_point_colname,
                                 pred_dist=pred_dist_colname,
                                 actual=actual_colname)

    def fit(self, X, treatment_colnames=None):
        """
        Fit a pricingengine estimator using the spcified treatment columns

        :param X: Training data
        :type X: TimeSeriesDataFrame

        :param treatment_colnames: 
            Names of columns to use as treatments in the Double ML procedure
            E.g. logarithm of price
            If a custom `double_ml_estimator` is passed to the constructor,
            the treatment will be identified there.
            In that case, this option will be ignored. 
        :type treatment_colnames: list of str

        :return: self
        :rtype: PricingEngineEstimator
        """

        # Make a default DML estimator if one isn't set
        if self.double_ml_estimator is None:
            if treatment_colnames is None or len(treatment_colnames) == 0:
                raise ValueError('No treatment column has been specified. '
                                 + 'Please set `treatment_colnames` option '
                                 + 'in the fit method or pass a custom '
                                 + 'DynamicDML object to the ' 
                                 + 'PricingEngineEstimator constructor.')
            schema = (PricingEngineEstimator
                      .make_pricingengine_schema(X, treatment_colnames))
            self.double_ml_estimator = (PricingEngineEstimator
                                        .pricingengine_dml_helper(schema))
        else:
            schema = self.double_ml_estimator._schema
        
        # Convert X to an EstimationDatset and call its fit method
        X_pe = PricingEngineEstimator.make_pricingengine_dataset(X, schema)
        self._double_ml_estimator.fit(X_pe)

        self._training_freq = X.infer_freq()
        self._training_cache = X.copy()

        return self

    def predict(self, X):
        """
        Generate "price-aware" forecasts 
        corresponding with each row in the input data frame.

        This method currently assumes that X has the same
        index structure and columns names as the training data.

        :param X: Input data (Scoring)
        :type X: TimeSeriesDataFrame

        :return: 
            Data frame that includes only the index of X, origin date/times,
            and point/distribution forecasts. None of the features 
            in X are returned.
        :rtype: ForecastDataFrame
        """

        try:
            # To-Do: What if X lacks some columns that are in training?
            # Like, the ts_value actuals, for instance?
            # In a true forecast, we don't know these!
            X_full = pd.concat([self._training_cache, X])
        except Exception as e:
            warn('Unable to prepend training features to prediction frame. '
                 + 'Forecasts may have missing values due to missing features. '
                 + 'Caught exception: ' + e.message, UserWarning)
            X_full = X

        schema = self.double_ml_estimator._schema
        X_pe = \
            PricingEngineEstimator.make_pricingengine_dataset(X_full, schema)
        preds_data = Predictions(self.double_ml_estimator, X_pe).data

        # Return a FDF representation
        return self._pricingengine_predictions_to_fdf(X, preds_data)

