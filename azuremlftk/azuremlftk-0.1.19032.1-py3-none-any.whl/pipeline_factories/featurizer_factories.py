from warnings import warn

from ftk.verify import is_iterable_but_not_string
from ftk.transforms import (TimeIndexFeaturizer, GrainIndexFeaturizer,
                            CategoryBinarizer, TimeSeriesImputer)
from ftk.pipeline import AzureMLForecastPipeline
from ftk.exception import TransformException

class FillMissingValuesFactory(object):
    """
    Create a pipeline for filling date gaps and missing values
    in a TimeSeriesDataFrame

    :param interpolate_fill: 
        List or dictionary of columns where interpolation should
        be used to fill missing values.
        When a dictionary is given, the keys are column names and
        the values are interpolation options (e.g. 'linear')
    :type interpolate_fill: list, dict

    :param value_fill:
        Dictionary of columns where missing values should be 
        filled with a constant value.
        Dictionary keys are column names, values are the constants
        that will fill the missing values.
    :type value_fill: dict
    """

    def __init__(self, interpolate_fill=None, value_fill=None,
                 create_indicator_features=True):

      self.interpolate_fill = interpolate_fill
      self.value_fill = value_fill

    @property
    def interpolate_fill(self):
        return self._interpolate_fill

    @interpolate_fill.setter
    def interpolate_fill(self, val):
        if val is None or isinstance(val, dict):
            self._interpolate_fill = val
        elif is_iterable_but_not_string(val):
            self._interpolate_fill = {col_name: 'linear' for col_name in val}
        else:
            raise TypeError('interpolate_fill must be a dict or list'
                            + 'instead got ' + type(val))

    @property
    def value_fill(self):
        return self._value_fill

    @value_fill.setter
    def value_fill(self, val):

        if val is not None and not isinstance(val, dict):
            raise TypeError('value_fill must be a dict '
                            + 'instead got ' + type(val))

        self._value_fill = val

    def build(self, X):
        """
        Build a date gap/missing value filling pipeline 
        """
        my_freq = X.infer_freq()

        steps = []
        if self.value_fill is not None:
            for col_name, val in self.value_fill.items():
                steps.append(('val_' + col_name,
                              TimeSeriesImputer(input_column=col_name,
                                                option='fillna',
                                                value=val,
                                                freq=my_freq)))

        if self.interpolate_fill is None:
            value_filled_cols = set(self.value_fill.keys()) \
                if self.value_fill is not None else set()
            numeric_cols = set(X.select_dtypes(include=['number']).columns) - \
                value_filled_cols

            interp_fill = {col: 'linear' for col in numeric_cols}
        else:
            interp_fill = self.interpolate_fill

        for col_name, method in interp_fill.items():
            steps.append(('interp_' + col_name,
                          TimeSeriesImputer(input_column=col_name, 
                                            option='interpolate',
                                            method=method,
                                            freq=my_freq)))
                
        return AzureMLForecastPipeline(steps=steps)


class BasicRegressionFeaturizerFactory(object):
    """
    Factory for building basic regression featurizer pipelines.

    This pipeline factory optionally creates the following steps, 
    in the specified order:
    1. Time index features
    2. Grain index features
    3. Horizon feature (when origin times are present in input frames)
    4. Binary (dummy) coding of categorical features

    :param time_index_features:
        If True, create a pipeline step with the `TimeIndexFeaturizer` 
        transform.
        The default TimeIndexFeaturizer options will be used.
    :type time_index_features: boolean

    :param grain_index_features:
        If True, create a pipeline step with the `GrainIndexFeaturizer` 
        transform
    :type grain_index_features: boolean

    :param horizon_feature:
        If `grain_index_features=True` and `horizon_feature=True`, 
        set `GrainIndexFeaturizer.make_horizon_feature=True` in the
        grain index featurizer pipeline step.
        This option is ignored if `grain_index_features=False`
    :type horizon_feature: boolean

    :param ts_freq:
        The frequency of the time series that the pipeline will be applied to.
        This parameter is used to construct the horizon feature.
        If `ts_freq=None`, the fit method will attempt to infer the frequency
        from the input TimeSeriesDataFrame.
    :type ts_freq: str (pandas offset alias), pd.DateOffset

    :param binary_encode:
        If True, create a `CategoryBinarizer` pipeline step to binary
        encode categorical features.
        The `CategoryBinarizer.drop_first` option is set to True in the
        created step, so the first level of each categorical feature will
        be dropped from the encoding.
    :type binary_encode: boolean

    :param categorical_features:
        Names of features that should be considered categorical. 
        If `binary_encode` is True,
        these features will be encoded by `CategoryBinarizer` step. 

        Note that the encoding step sets 
        `CategoryBinarizer.encode_all_categoricals` to True, so the encoder
        will encode `categorical_features` as well as other features that have
        data types indicated categorical type.
    """
    def __init__(self, time_index_features=True,
                 grain_index_features=True,
                 horizon_feature=True,
                 ts_freq=None,
                 binary_encode=True,
                 categorical_features=None):
        
        self.time_index_features = time_index_features
        self.grain_index_features = grain_index_features
        self.horizon_feature = horizon_feature
        self.binary_encode = binary_encode
        self.categorical_features = categorical_features
        self.ts_freq = ts_freq

    @property
    def categorical_features(self):
        """
        List of features that should be considered categorical
        """
        return self._categorical_features

    @categorical_features.setter
    def categorical_features(self, cat_features):

        if is_iterable_but_not_string(cat_features):
            if all(isinstance(f, str) for f in cat_features):
                # Cast to set to remove duplicates
                self._categorical_features = list(set(cat_features))
            else:
                raise TransformException(
                    'features column names must all be strings.')

        elif isinstance(cat_features, str):
            self._categorical_features = [cat_features]

        elif cat_features is None:
            self._categorical_features = None

        else:
            raise TransformException('features column names can be None, '
                                     + 'a string, or an iterable containing strings')
    def build(self, X):
        """
        Build a featurizer pipeline.

        :param X: 
            Input data frame. Some pipeline steps may need to inspect
            the data frame columns as part of their construction.
            E.g. a horizon feature is only made if origin times
            are present in the data frame. 
        :type X: TimeSeriesDataFrame

        :return: Pipeline
        :rtype: AzureMLForecastPipeline
        """
        steps = list()
        if self.time_index_features:
            steps.append(('time_features', 
                          TimeIndexFeaturizer(overwrite_columns=True)))

        if self.grain_index_features:
            if self.horizon_feature and X.origin_time_colname is None:
                warn(type(self).__name__ + '.build: '
                     + 'Dataframe lacks origin times; horizon feature '
                     + 'cannot be created.', UserWarning)
            make_hrzon_feat = (X.origin_time_colname is not None 
                               and self.horizon_feature)
            grain_featurizer = GrainIndexFeaturizer(
                    make_horizon_feature=make_hrzon_feat, 
                    ts_frequency=self.ts_freq,
                    overwrite_columns=True)
            steps.append(('grain_features', grain_featurizer))

        if self.binary_encode:
            steps.append(('dummy_coder', 
                          CategoryBinarizer(columns=self.categorical_features,
                                            encode_all_categoricals=True,
                                            drop_first=True)))

        if len(steps) == 0:
            raise TransformException(
                'Bad factory configuration; pipeline has no steps.')

        return AzureMLForecastPipeline(steps=steps)

