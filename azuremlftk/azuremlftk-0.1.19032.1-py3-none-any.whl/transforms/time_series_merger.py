"""
Merge (join) in other time series, respecting the time index. 
"""

from pandas import DataFrame

from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.pipeline import AzureMLForecastPipeline


class TimeSeriesMerger(AzureMLForecastTransformerBase):
    """
    .. py:class:: TimeSeriesMerger
    A transformation class for merging an external DataFrame with the
    transform input.
    
    Objects of this class can be used independently or included as steps in
    a forecast pipeline.

    :param right:
        Dataframe which will be merged to input of the tranform function
    :type right: pandas.DataFrame

    :param how:
        One of {'left', 'right', 'outer', 'inner'}.
        * left: use only keys from left frame, similar to a SQL left outer
          join; preserve key order
        * right: use only keys from right frame, similar to a SQL right outer
          join; preserve key order
        * outer: use union of keys from both frames, similar to a SQL full
          outer join; sort keys lexicographically
        * inner: use intersection of keys from both frames, similar to a SQL
          inner join; preserve the order of the left keys
    :type how: str

    :param on:
        Field names to join on. Must be found in both DataFrames. If on is
        None and not merging on indexes, then it merges on the intersection
        of the columns by default.
    :type on: str, list

    :param left_on:
        Field names to join on in left DataFrame. Can be a vector or list of
        vectors of the length of the DataFrame to use a particular vector as
        the join key instead of columns
    :type left_on: str, list, or array-like

    :param right_on:
        Field names to join on in right DataFrame or vector/list of vectors
        per left_on docs
    :type right_on: str, list, or array-like

    :param left_index:
        Use the index from the left DataFrame as the join key(s). If it is a
        MultiIndex, the number of keys in the other DataFrame (either the
        index or a number of columns) must match the number of levels
        in the MultiIndex
    :type left_index: boolean, default False
    :param right_index:
        Use the index from the right DataFrame as the join key. Same caveats
        as left_index
    :type right_index: boolean, default False
    :param sort:
        Sort the join keys lexicographically in the result DataFrame. If
        False, the order of the join keys depends on the join type (how
        keyword)
    :type sort: boolean, default True
    :param suffixes:
        Suffix to apply to overlapping column names in the left and right
        side, respectively
    :type suffixes: 2-length sequence (tuple, list, ...)
    :param copy:
        If False, do not copy data unnecessarily
    :type copy: boolean, default True
    :param indicator:
        If True, adds a column to output DataFrame called "_merge" with
        information on the source of each row.
        If string, column with information on source of each row will be
        added to output DataFrame, and column will be named value of string.
        Information column is Categorical-type and takes on a value of "left
        _only" for observations whose merge key only appears in 'left'
        DataFrame,
        "right_only" for observations whose merge key only appears in
        'right' DataFrame, and "both" if the observation's merge key is
        found in both.
    :type indicator: boolean or string, default False
    :param dropna:
        If True, drop the rows with Nan values in the merge result.
        Default options in pandas.DataFrame.dropna are used. To use
        non-default options, use the DropNA transformer.
    :type dropna: boolean
   
    """

    def __init__(self, right, how='inner', on=None, left_on=None, right_on=None,
                 left_index=False, right_index=False, sort=True,
                 suffixes=('_x', '_y'), copy=True, indicator=False,
                 dropna=False):
        if isinstance(right, AzureMLForecastPipeline):
            #TODO: construct right object by executing input pipeline
            raise NotImplementedError(
                'Joining two pipelines is not supported yet.')
        elif isinstance(right, DataFrame):
            self.right = right
        else:
            raise TypeError('The type of the right object of TSMerger must be '
                            'TimeSeriesDataFrame, pandas.DataFrame, '
                            'or AzureMLForecastPipeline')
        self.how = how
        self.on = on
        self.left_on = left_on
        self.right_on = right_on
        self.left_index = left_index
        self.right_index = right_index
        self.sort = sort
        self.suffixes = suffixes
        self.copy = copy
        self.indicator = indicator
        self.dropna = dropna

    @loggable
    def fit(self, X, y=None):
        """
        Fit is empty for this transform; this method is just a pass-through

        :param X: Ignored.

        :param y: Ignored.

        :return: self
        :rtype: TimeSeriesMerger
        """
        return self

    @loggable
    def transform(self, X):
        """
        Merge the data frame, `X`, with the
        external data frame, `right`.

        :param X: Data frame to transform
        :type X: pandas.DataFrame

        :return: A data frame resulting from the merge
        :rtype: pandas.DataFrame
        """
        merge_result = X.merge(right=self.right, how=self.how, on=self.on,
                               left_on=self.left_on, right_on=self.right_on,
                               left_index=self.left_index,
                               right_index=self.right_index, sort=self.sort,
                               suffixes=self.suffixes, copy=self.copy,
                               indicator=self.indicator)
        if self.dropna:
            merge_result.dropna(inplace=True)

        return merge_result
