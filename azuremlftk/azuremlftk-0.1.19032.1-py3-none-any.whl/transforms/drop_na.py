"""
Remove rows or columns with Nan values.
"""

from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.exception import TransformException
from ftk.verify import is_iterable_but_not_string

class DropNA(AzureMLForecastTransformerBase):
    """
    .. py:class:: DropNA
    A transformation class for removing rows or columns with Nan values.

    .. _pandas.DataFrame.dropna: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.dropna.html

    Objects of this class can be used independently or included as steps in
    a forecast pipeline.

    :param axis:
         {0 or 'index', 1 or 'columns'}, default 0
         Determine if rows or columns which contain missing values are removed.
         0, or 'index' : Drop rows which contain missing values.
         1, or 'columns' : Drop columns which contain missing value.
    :type axis: int, str

    :param how:
        {'any', 'all'}, default 'any'
        Determine if row or column is removed from DataFrame, when we have
        at least one NA or all NA.
        'any' : Remove the row/column if there is at least one NA entry.
        'all' : remove the row/column if all of the entries are NA.
    :type how: str

    :param thresh:
        Require that many non-NA values to remove a row or column.
        Note: the `how` argument is ignored when `thresh` is set.
    :type thresh: int

    :param subset:
        Labels along other axis to consider to restrict the drop operation
        to a subset of rows or columns, e.g. if you are dropping
        rows, these would be a list of columns to include.
    :type subset: array-like

    :param inplace: If True, do operation inplace.
    :type: inplace: boolean
    """

    def __init__(self, axis=0, how='any', thresh=None, subset=None,
                 inplace=False):
        self.axis = axis
        self.how = how
        self.thresh = thresh
        self.subset = subset
        self.inplace = inplace

        self._na_columns = []
        self._is_fit = False

    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, val):
        valid_axis_values = [0, 1, 'index', 'columns']
        if val in valid_axis_values:
            self._axis = val
        else:
            raise ValueError('"{0}" is an invalid value for the "axis" '
                             'argument. Valid values are: {1}'
                             .format(val, valid_axis_values))

    @property
    def how(self):
        return self._how

    @how.setter
    def how(self, val):
        valid_how_values = ['any', 'all']
        if val in valid_how_values:
            self._how = val
        else:
            raise ValueError('"{0}" is an invalid value for the "how" '
                             'argument. Valid values are: {1}'
                             .format(val, valid_how_values))

    @property
    def thresh(self):
        return self._thresh

    @thresh.setter
    def thresh(self, val):
        if val is not None:
            if isinstance(val, int):
                self._thresh = val
            else:
                raise ValueError('The "thresh" argument expects an integer '
                                 'value, {0} is passed instead.'
                                 .format(type(val)))
        else:
            self._thresh = val

    @property
    def subset(self):
        return self._subset

    @subset.setter
    def subset(self, val):
        if val is not None:
            if is_iterable_but_not_string(val):
                self._subset = val
            else:
                raise ValueError('The "subset" argument expects an array-like '
                                 'value, {0} is passed instead.'
                                 .format(type(val)))
        else:
            self._subset = val

    @property
    def inplace(self):
        return self._inplace

    @inplace.setter
    def inplace(self, val):
        if isinstance(val, bool):
            self._inplace = val
        else:
            raise ValueError('The "inplace" argument expects a boolean '
                             'value, {0} is passed instead.'.format(type(val)))

    def _get_na_columns(self, X):
        """
        This function returns the column names with Nan values.
        """
        if self.subset is not None:
            notnull_by_column = X[self.subset].notnull()
        else:
            columns_to_check = list(X.columns)
            # We can not drop the target column
            if X.ts_value_colname:
                columns_to_check.remove(X.ts_value_colname)
            notnull_by_column = X[columns_to_check].notnull()

        na_columns = []
        if self.thresh is not None:
            for c in notnull_by_column.columns:
                if (notnull_by_column[c] == False).sum() >= self.thresh:
                    na_columns.append(c)
        else:
            if self.how == 'any':
                for c in notnull_by_column.columns:
                    if not notnull_by_column[c].all():
                        na_columns.append(c)
            elif self.how == 'all':
                for c in notnull_by_column.columns:
                    if not notnull_by_column[c].any():
                        na_columns.append(c)

        return na_columns

    def _drop_na_columns(self, X):
        if self.inplace:
            X.drop(self._na_columns, axis=1, inplace=self.inplace)
        else:
            X = X.drop(self._na_columns, axis=1)

        return X

    def _drop_na_rows(self, X):
        if self.inplace:
            X.dropna(axis=self.axis, how=self.how, thresh=self.thresh,
                     subset=self.subset, inplace=self.inplace)
        else:
            X = X.dropna(axis=self.axis, how=self.how, thresh=self.thresh,
                         subset=self.subset, inplace=self.inplace)

        return X

    @loggable
    def fit(self, X, y=None):
        """
        When dropping columns with Nan values, the fit method finds the
        columns with Nan values and records them to be used in the transform
        method.
        When dropping rows with Nan values, the fit method only marks the
        transformer as fitted.

        :param X: Input data
        :type X: TimeSeriesDataFrame

        :param y: Ignored. Included for pipeline compatibility

        :return: Fitted transformer
        :rtype: DropNA
        """
        if self.axis == 1 or self.axis == 'columns':
            self._na_columns = self._get_na_columns(X)
        self._is_fit = True

        return self

    @loggable
    def transform(self, X):
        """
        Remove rows or columns with Nan values.

        :param X: Data frame to transform.
        :type X: TimeSeriesDataFrame

        :return: Transformed data.
        :rtype: TimeSeriesDataFrame
        """
        if self.axis == 1 or self.axis == 'columns':
            if not self._is_fit:
                raise TransformException('The DropNA transformer must be '
                                         'fitted when dropping columns.')
            na_columns_cur = self._get_na_columns(X)
            extra_na_columns = set(na_columns_cur)\
                .difference(set(self._na_columns))
            if len(extra_na_columns) > 0:
                raise TransformException('The data frame contains extra '
                                         'columns with nan values, which '
                                         'are not dropped in the training '
                                         'data. Use DropColumns transformer '
                                         'to drop these columns in the '
                                         'training data or use '
                                         'TimeSeriesImputer to impute these '
                                         'columns in the data frame. The '
                                         'columns are: {0}'
                                         .format(extra_na_columns))

            result = self._drop_na_columns(X)
        else:
            result = self._drop_na_rows(X)

        return result

    @loggable
    def fit_transform(self, X, y):
        """
        This method is equivalent to first calling `fit` and then calling
        `transform` on X. It's more efficient for dropping columns on
        training data, because it only checks for columns with Nan values
        once, while calling `fit` and `transform` separately checks twice.

        :param X: Input data
        :type X: TimeSeriesDataFrame

        :param y: Ignored. Included for pipeline compatibility

        :return: Transformed data.
        :rtype: TimeSeriesDataFrame
        """

        if self.axis == 1 or self.axis == 'columns':
            self._na_columns = self._get_na_columns(X)
            result = self._drop_na_columns(X)
        else:
            result = self._drop_na_rows(X)

        self._is_fit = True

        return result