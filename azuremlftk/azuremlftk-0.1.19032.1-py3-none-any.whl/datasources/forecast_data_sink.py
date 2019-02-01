import numpy as np
import abc

from ftk.datasources import DataTransformerMixin
from ftk.base_estimator import AzureMLForecastTransformerBase
from ftk import TimeSeriesDataFrame, ForecastDataFrame


class ForecastDataSink(DataTransformerMixin):
    """
    The abstract class to serialize the time series data frames to the data base.
    
    Forecast<StorageType>DataSource classes read data from external storage.
    Forecast<StorageType>DataSink classes write data to external storage.
    They are inherited from DataTransformerMixin which implements the abstract method transform() and exact methods fit(), fit_transform(), predict() from the Transformer interface.
    SQLDataManager abstracts out the database connection capability for both ForecastSQLDataSource and ForecastSQLDataSink, which inherit from it.
    ForecastDataSource and ForecastDataSink abstract reconstruction of TimeSeriesDataFrame from the pandas.DataFrame and serialization of TimeSeriesDataFrame
    back to pandas.DataFrame of given the metadata provided by user. If the metadata were not provided the plane pandas.DataFrame
    will be loaded or saved.
    
    :param table: The name of a table to store the data
    :type table: str
    :param connection_str: The connection string to the database
    :type connection_str: str
    :param dialect: The sqlalchemy dialect+driver. The default is mssql+pyodbc
                    other possible drivers are: mysql, oracle, mssql+pymssql, sqlite, postgresql.
    :type dialect: str
    :param clean_df_after_sink: if True the transform will return the.
    :type clean_df_after_sink: bool
    :param add_index_as_column: If True, index column from the data frame will be added as a column. 
                                Otherwise it will be dropped.
    :type add_index_as_column: bool
    :param run_tag: Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                    The run_tag column will be dropped from the output DataFrame.
                    Run identifier may not be longer then 255 symbols.
                    If user explicitly set run tag (in transform(), by setting it on the object or parameter on the pipeline,
                    it is used to save the data. If this parameter is not set by user, it will be set to the current time stamp
                    each time the transform() runs.
    :type run_tag: str
    
    """
    def __init__(self,
                 clean_df_after_sink = False,
                 run_tag=None):
        """
        Constructor
        
        """
        self._clean_df_after_sink = clean_df_after_sink
        super(ForecastDataSink, self).__init__(run_tag=run_tag)
        
    def transform(self, X:TimeSeriesDataFrame, **kwargs):    
        """
        Write data to SQL database.
        If X is connection info, then ignore connection string
        provided in constructor and use that.
        NOTE: if X is ForecastDataFrame the pred_dist column is dropped, because it
        contains distribution, which can not be serialized.
        
        :param X: the data frame which needs to be sinked to the database.
        :type X: DataFrame
        :param run_tag: The pipeline run identifier to be used to upload or download data.
                        If the run_tag is not None, the new table will be appended to the existing one.
                        In this case the value of if_exists will be ignored.
                        If the existing table already has the records with the run_tag, these records will be deleted.
                        Run identifier may not be longer then 255 symbols.
        :type run_tag: str
        :returns: the table with data.
        :rtype: pandas.DataFrame
        
        """
        initial_data  = X
        if isinstance(X, ForecastDataFrame) and not X.pred_dist is None:
            #The Predicted distribution represents a distribution and can not be serialized.
            #create the dummy column and fill it with
            dist_col = X.pred_dist
            X = X.drop(X.pred_dist, axis=1, inplace=False)
            X = X.assign(**{dist_col:np.nan})
            #Restore the column order.
            X = X.reindex(columns=initial_data.columns)
        #Time series data frame has multi index, which is not properly understood by SQL.
        data = X
        if isinstance(X, TimeSeriesDataFrame):
            data = X._extract_time_series(colnames=X.columns.values).reset_index()
            if not X.origin_time_colname is None:
                data[X.origin_time_colname] = X.origin_time_index
        self.set_tag_from_params(**kwargs)
        self.save_data(data, **kwargs)
        if self._clean_df_after_sink:
            return initial_data.iloc[0:0]
        return initial_data
    
    @abc.abstractmethod
    def save_data(self, X, **kwargs):
        """
        The method used to save the data.
        
        :param data: The data frame to be saved.
        :type data: pandas.DataFrame
        
        """
        pass
        
        