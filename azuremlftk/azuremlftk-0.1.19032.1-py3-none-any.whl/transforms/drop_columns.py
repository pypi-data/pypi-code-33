"""
Drop columns from dataset.
"""

from ftk import verify
from ftk.base_estimator import AzureMLForecastTransformerBase, loggable
from ftk.time_series_data_frame import TimeSeriesDataFrame
from ftk.exception import NotTimeSeriesDataFrameException
from ftk.verify import Messages
from warnings import warn

class DropColumns(AzureMLForecastTransformerBase):
    """
    .. py:class:: DropColumns
    A transform class for dropping columns from a TimeSeriesDataFrame.

    Metadata columns (grain, value, time_index, group) cannot be dropped.

    :param drop_columns: list of names of columns to be dropped
    :type drop_columns: list

    """

    def __init__(self, drop_columns):
        self.drop_columns = drop_columns
        
    @property
    def drop_columns(self):
        """
        List of column names to drop.
        """
        return self._drop_columns

    @drop_columns.setter
    def drop_columns(self, val):
        if verify.is_iterable_but_not_string(val):
            self._drop_columns = val
        else:
            self._drop_columns = [val]

        if not all(isinstance(col, str) for col in self._drop_columns):
            raise TypeError('drop_columns must be strings.')


    def _check_columns_against_input(self, X):
        """
        Check the list of columns to drop.
        Exclude columns that are not in X or are properties 
        of X (grain, group, time_index, value).

        :param X: is a TimeSeriesDataFrame
        :returns: a list of valid column labels to drop.

        """

        # Need to check against tsdf properties
        # Concat properties (as lists) into a list 
        properties = [item if verify.is_iterable_but_not_string(item) 
                      else [item] 
                      for item in (X.grain_colnames, X.time_colname, 
                                   X.ts_value_colname, X.group_colnames)]

        # We will not check against _metadata. 
        # This transform will be willing to drop important metadata columns 
        # from subclasses (ForecastDataFrame, MultiForecastDataFrame).
        # However, they are *outputs* we do not wish to lock down as tightly.

        # Flatten the list of properties to a list of column names
        properties_colnames = [item for sublist in properties
                               for item in sublist]
        
        # Filter out columns we can't drop
        drop_columns_safe = [col for col in self._drop_columns
                             if col in X.columns
                             and col not in properties_colnames]

        if len(self._drop_columns) != len(drop_columns_safe):
            warn('One or more requested columns will not be dropped. '\
                + 'Cannot drop nonexistent columns or TimeSeriesDataFrame '\
                + 'property columns (grain_colnames, time_colname, '\
                + 'ts_value_colname, group_colnames)')
        
        return drop_columns_safe
    
    @loggable
    def fit(self, X, y=None):
        """
        Fit is empty for this transform; this method is just a pass-through

        :param X: Ignored.

        :param y: Ignored.

        :return: self
        :rtype: DropColumns
        """
        return self

    @loggable
    def transform(self, X):
        """
        Drop the columns from dataframe.

        :param X: Input data
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :return: Data with columns dropped.
        :rtype: :class:`ftk.dateframets.TimeSeriesDataFrame`

        """

        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                Messages.XFORM_INPUT_IS_NOT_TIMESERIESDATAFRAME)

        drop_labels = self._check_columns_against_input(X) 
        X_new = X.drop(drop_labels, axis=1)

        return X_new

