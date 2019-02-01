"""
Wrap any scikit-style transformer and use it in the forecast pipeline.
"""

import numpy as np
import scipy
import pandas as pd
from warnings import warn
from sklearn.preprocessing import (StandardScaler, OneHotEncoder, 
                                   QuantileTransformer, PolynomialFeatures)
from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.base_estimator import AzureMLForecastTransformerBase, loggable

NotTimeSeriesDataFrameException = TypeError('The input X is not a TimeSeriesDataFrame.')

_label_related_transform = ['LabelBinarizer', 'LabelEncoder']

class SklearnTransformerWrapper(AzureMLForecastTransformerBase):

    """
    .. py:class:: SklearnTransformerWrapper
    A transformer class that creates wrappers for scikit-learn transformers
    that conduct corresponding transformations on TimeSeriesDataFrame.

    .. _sklearn.base.TransformerMixin: http://scikit-learn.org/stable/modules/
                        generated/sklearn.base.TransformerMixin.html

    :param sklearntransformer: any transformer in scikit-learn
        The transformers in scikit-learn usually inherit from
        sklearn.base.TransformerMixin, and have fit() and
        transform() method implemented.
    :type sklearntransformer: sklearn.base.TransformerMixin

    :param input_column:
        The input column(s) where the transformation is conducted on.
    :type input_column: str, list, array-like

    :param output_column_suffix:
        This is the suffix will be added to the names of the transformed
        columns. The default option is None, which will overwrite the current
        input columns. You can also specify the output_column_sufffix as
        'default', which will have the suffix of the output columns equal to
        the scikit-learn transformer type. If you provide custom string here,
        the provided string will be used as the suffix for the output column
        names.

        .. note:: This parameter only will apply when the transformation is
            one-to-one mapping, i.e, for each column in the input columns,
            there will be exactly one corresponding transformed column in the
            output TimeSeriesDataFrame. Some counter examples would be the
            transformations conducting one-to-many mapping, e.g OneHotEncoder,
            or transformations conducting many-to-many mapping, e.g
            PolynomialFeatures. For the counter examples, the names of the
            transformed columns will be handled properly by default.
    :type output_column_suffix: str

        
    :param drop_original:
        If True, the original input columns will be dropped from the input
        TimeSeriesDataFrame, vice versa.

        .. note:: The columns in TimeSeriesDataFrame.grain and
            TimeSeriesDataFrame.time_index will never be dropped since they
            contain important meta information.
    :type drop_original: boolean

    Examples:

    >>> data1 = {'store': [1, 2, 3], 'brand': ['a', 'b', 'c'], 'feature1':
    ...         [0,1,0], 'feature2':[5,8,2],
    ...         'date': pd.to_datetime(['2017-01-01', '2017-01-02',
    ...         '2017-01-03']),
    ...         'sales': [3, 6, 7]}
    >>> timeseries_df1 = TimeSeriesDataFrame(data1, grain=['store','brand'],
    ...                     time_index='date', value='sales')
    >>> timeseries_df1
      brand       date  feature1  feature2  sales  store
    0     a 2017-01-01         0         5      3      1
    1     b 2017-01-02         1         8      6      2
    2     c 2017-01-03         0         2      7      3

    Wrapper for StandardScaler:

    >>> scaler = StandardScaler()
    >>> scaler_dfwrapper = SklearnTransformerWrapper(scaler, input_column=
    ...   ['feature1', 'feature2'], output_column_suffix=None, drop_original=True)
    >>> scaler_dfwrapper.fit_transform(timeseries_df1)
      brand       date  feature1  feature2  sales  store
    0     a 2017-01-01 -0.707107  0.000000      3      1
    1     b 2017-01-02  1.414214  1.224745      6      2
    2     c 2017-01-03 -0.707107 -1.224745      7      3

    Wrapper for OneHotEncoder:

    >>> enc = OneHotEncoder()
    >>> enc_dfwrapper = SklearnTransformerWrapper(enc, input_column='feature1',
    ...    output_column_suffix=None, drop_original=True)
    >>> enc_dfwrapper = enc_dfwrapper.fit(timeseries_df1)
    >>> enc_dfwrapper.transform(timeseries_df1)
      brand       date  feature2  sales  store  feature1_0  feature1_1
    0     a 2017-01-01         5      3      1         1.0         0.0
    1     b 2017-01-02         8      6      2         0.0         1.0
    2     c 2017-01-03         2      7      3         1.0         0.0

    Wrapper for QuantileTransformer:

    >>> qt = QuantileTransformer(random_state=0)
    >>> qt_dfwrapper = SklearnTransformerWrapper(qt, input_column=['feature2'],
    ...    output_column_suffix='default', drop_original=False)
    >>> qt_dfwrapper.fit_transform(timeseries_df1)
      brand       date  feature1  feature2  sales  store
    0     a 2017-01-01         0         5      3      1
    1     b 2017-01-02         1         8      6      2
    2     c 2017-01-03         0         2      7      3
    >>>   feature2_QuantileTransformer
    0                  5.000000e-01
    1                  9.999999e-01
    2                  1.000000e-07

    Wrapper for PolynomialFeatures:

    >>> poly = PolynomialFeatures(2)
    >>> poly_dfwrapper = SklearnTransformerWrapper(poly, input_column=
    ...    ['feature1', 'feature2'], output_column_suffix=None,
    ...     drop_original=True)
    >>> poly_dfwrapper.fit_transform(timeseries_df1)
      brand       date  sales  store  PolynomialFeatures_0  PolynomialFeatures_1
    0     a 2017-01-01      3      1                   1.0                   0.0
    1     b 2017-01-02      6      2                   1.0                   1.0
    2     c 2017-01-03      7      3                   1.0                   0.0
    >>>   PolynomialFeatures_2  PolynomialFeatures_3  PolynomialFeatures_4
    0                   5.0                   0.0                   0.0
    1                   8.0                   1.0                   8.0
    2                   2.0                   0.0                   0.0
    >>>  PolynomialFeatures_5
    0                  25.0
    1                  64.0
    2                   4.0

    """

    def __init__(self, sklearntransformer, input_column, output_column_suffix=None, drop_original=False):
        self._sklearntransformer = sklearntransformer

        if isinstance(input_column, str):
            self._input_column = [input_column]
        else:
            self._input_column = input_column

        if output_column_suffix=='default':
            self._output_column_suffix = type(sklearntransformer).__name__
        else:
            self._output_column_suffix = output_column_suffix

        self._drop_original = drop_original


    @property
    def sklearntransformer(self):
        """
        Internal scikit-learn transform
        """
        return(self._sklearntransformer)

    @property
    def input_column(self):
        """
        Column name or list of column names to transform
        """
        return(self._input_column)

    @property
    def output_column_suffix(self):
        """
        See `output_column_suffix` parameter
        """
        return(self._output_column_suffix)

    @property
    def drop_original(self):
        """
        See `drop_original` parameter
        """
        return(self._drop_original)

    def _check_columns(self, X):
        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException
        
        # must check that parts of index are not requested for transform
        input_columns_in_index = [cl for cl in self._input_column 
                                  if cl in list(X.index.names)]
        if len(input_columns_in_index) > 0:
            error_message = 'Cannot transform input column(s) which are ' + \
              'part of MultiIndex in the input dataframe: {0}'.format(
                  input_columns_in_index)
            raise ValueError(error_message)

        # check that columns that are asked to be transformed 
        # exist in time series data frame
        input_column_not_in_X = [cl for cl in self._input_column 
                                 if cl not in X.columns]
        if len(input_column_not_in_X) > 0:
            error_message = 'The input column(s) do not exist in the ' + \
              'input dataframe: {0}'.format(input_column_not_in_X)
            raise ValueError(error_message)

    @loggable
    def fit(self, X, y=None, **fit_params):
        """
        Fit the transform.

        This method calls the `fit` method of the internal
        scikit-learn transformer

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :param y: Passed on to sklearn transformer fit

        :return: Fitted transform
        :rtype: SklearnTransformerWrapper
        """
        self._check_columns(X)
        if type(self._sklearntransformer).__name__ in (_label_related_transform):
            if len(self._input_column) > 1:
                raise ValueError('LabelEncoder accept only one column as input.')
            self._sklearntransformer.fit(X[self._input_column[0]], **fit_params)
        else:
            self._sklearntransformer.fit(X[self._input_column], y, **fit_params)
        return self

    @loggable
    def transform(self, X):
        """
        Apply the internal scikit-learn transformer

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :return: Data frame with transform applied
        :rtype: :class:`ftk.dateframets.TimeSeriesDataFrame`
        """
        X = X.copy()
        self._check_columns(X)
        if type(self._sklearntransformer).__name__ in (_label_related_transform):
            output_X = self._sklearntransformer.transform(X[self._input_column[0]])
            output_X = output_X.reshape(output_X.shape[0], 1)
        else:
            output_X = self._sklearntransformer.transform(X[self._input_column])

        if output_X.shape[0] != X.shape[0]:
            raise ValueError('The transformation output must have the same row as that of the input dataframe, '
                             'the transformation output has {0} rows, while the input dataframe has {1} rows.'.format(
                output_X.shape[0], X.shape[0]))

        if type(self._sklearntransformer).__name__ in ['OneHotEncoder']:
            output_column_name = [cl+'_'+str(j) for i, cl in enumerate(self._input_column) for j in range(self._sklearntransformer.n_values_[i])]
        else:
            if output_X.shape[1]==len(self._input_column):
                if self._output_column_suffix is None:
                    output_column_name = self._input_column
                    self._drop_original = False
                else:
                    output_column_name = [(cl + '_' +self._output_column_suffix) for cl in self._input_column]
            else:
                output_column_name = [(type(self._sklearntransformer).__name__ + '_' + str(n)) for n in range(output_X.shape[1])]

        if isinstance(output_X, scipy.sparse.csr.csr_matrix):
            output_X = output_X.toarray()

        X[output_column_name] = pd.DataFrame(output_X, index=X.index)

        if self._drop_original:
            # will not drop the columns in grain, time_index of the TimeSeriesDataFrame
            column_to_drop = [cl for cl in self._input_column if (cl not in X.time_colname)
                              and (cl not in X.grain_colnames)]
            X = X.drop(column_to_drop, axis=1)

        return(X)





