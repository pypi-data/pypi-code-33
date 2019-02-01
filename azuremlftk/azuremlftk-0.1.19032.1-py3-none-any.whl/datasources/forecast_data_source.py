import pandas as pd
import numpy as np
import warnings
from abc import abstractmethod

from ftk.datasources import DataTransformerMixin
from ftk.base_estimator import AzureMLForecastTransformerBase
from ftk import TimeSeriesDataFrame, ForecastDataFrame, MultiForecastDataFrame

class ForecastDataSource(DataTransformerMixin):
    """
    The wrapper of the DataTransformerMixin, which returns the TimeSeriesDataFrame
    or ForecastDataFrame if it has the metadata.
    
    Forecast<StorageType>DataSource classes read data from external storage.
    Forecast<StorageType>DataSink classes write data to external storage.
    They are inherited from DataTransformerMixin which implements the abstract method transform() and exact methods fit(), fit_transform(), predict() from the Transformer interface.
    SQLDataManager abstracts out the database connection capability for both ForecastSQLDataSource and ForecastSQLDataSink, which inherit from it.
    ForecastDataSource and ForecastDataSink abstract reconstruction of TimeSeriesDataFrame from the pandas.DataFrame and serialization of TimeSeriesDataFrame
    back to pandas.DataFrame of given the metadata provided by user. If the metadata were not provided the plane pandas.DataFrame
    will be loaded or saved.
    
    :param time_colname: The time_colname to create TimeSeriesDataFrame.
    :type time_colname: str
    :param grain_colnames: The grain colnames to create TimeSeriesDataFrame.
    :type grain_colnames: list
    :param ts_value_colname: The Time series value column name.
    :type ts_value_colname: str
    :param origin_time_colname: The column name for the origin time to create TimeSeriesDataFrame. 
    :type origin_time_colname: str
    :param pred_point: The point forecast column name. The metadata fore ForecastDataFrame. 
    :type pred_point: str
    :param pred_dist: The distribution forecast column name. The metadata for ForecastDataFrame.
    :type pred_dist: str
    :param model_colnames: The name of model colname. The metadata for MultiForecastDataFrame.
    :type model_colnames: list
    :param deduplicate: Deduplicate the index.
    :type deduplicate: bool
    :param run_tag: Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                    The run_tag column will be dropped from the output DataFrame.
                    Run identifier may not be longer then 255 symbols.
    :type run_tag: str
    
    """
    def __init__(self, 
                 time_colname:str=None,
                 grain_colnames=None,
                 ts_value_colname=None,
                 origin_time_colname=None,
                 pred_point=None,
                 pred_dist=None,
                 model_colnames=None,
                 deduplicate=False,
                 run_tag=None):
        """
        Constructor.
        
        """
        self._time_colname = time_colname
        self._grain_colnames = grain_colnames
        self._ts_value_colname=ts_value_colname
        self._origin_time_colname=origin_time_colname
        self._pred_point=pred_point
        self._pred_dist=pred_dist
        self._model_colnames=model_colnames
        self._dedup = deduplicate
        super(ForecastDataSource, self).__init__(run_tag=run_tag)
    
    def transform(self, X=None, **kwargs):
        """
        Retrieve the data from the SQL database abd convert it to 
        TimeSeriesDataFrame, ForecastDataFrame or MultiForecastDataFrame depending on metadata presence.
        If X is connection info, then ignore connection string
        provided in constructor and use that.
        If there is no time colname provided the value error is raised.
        The set of columns and possible values also can be given for the purpose of data frame filtering.
        For example: transform(X=None, run_tag='run1', location=['Mars', 'Venus'], life_form=['mold'])
        will take only data with the tuples with values of location equal to Mars and Venus and life_form equals to mol
        
        :param X: Connection string.
        :type X: str
        :param run_tag: The pipeline run identifier to be used retrieve data only matching the tag.
                        If run_tag is None, all records will be returned.
                        Run identifier may not be longer then 255 symbols.
        :type run_tag: str
        :returns: the table with data.
        :rtype: TimeSeriesDataFrame, ForecastDataFrame or MultiForecastDataFrame
        :rises: ValueError
        
        """
        if kwargs.get(DataTransformerMixin.TAG_VAR) is None and not self._run_tag is None:
            kwargs[DataTransformerMixin.TAG_VAR] = self._run_tag
        data =  self.load_data(X, **kwargs)
        if not self._time_colname:
            #If there is no time column name, return pandas.DataFrame.
            return data
        if self._time_colname and not self._time_colname in list(data.columns.values):
            raise ValueError("The column name {} was not found in the remote table.".format(self._time_colname))
        #Try to convert time column to the datetime format
        if self._time_colname and data[self._time_colname].dtype=='int64':
            data[self._time_colname] = pd.to_datetime(data[self._time_colname], unit='ms')
        data[self._time_colname] = pd.to_datetime(data[self._time_colname])
        data.set_index([self._time_colname] + self._grain_colnames, inplace=True)
        dedupl_series = data.index.duplicated(keep='first')
        if self._dedup and dedupl_series.any():
            warnings.warn('Duplicates were found, removing as instructed. Check data!')
            data = data[~dedupl_series];
        data_ts = TimeSeriesDataFrame(data = data,
                                      time_colname=self._time_colname,
                                      grain_colnames=self._grain_colnames,
                                      ts_value_colname=self._ts_value_colname,
                                      origin_time_colname=self._origin_time_colname)
        
            
        if self._pred_point is None:
            return data_ts
        #The distribution forecast column can not be serialized to the table.
        #If the table contains ForecastDataFrame we need to create the dummy column.
        data_ts = self.assign_column_maybe(data_ts, self._pred_dist, use_zeroes=False)
        if data_ts[self._pred_dist].isnull().all():
            #Fix wrong type returned from SQL.
            data_ts = data_ts.assign(**{self._pred_dist:np.nan})
        #If the forecast column does not exist, create it.
        data_ts = self.assign_column_maybe(data_ts, self._pred_point)

        data_fdf = ForecastDataFrame(data = data_ts,
                                     pred_point = self._pred_point,
                                     pred_dist = self._pred_dist)
        if self._model_colnames is None:
            return data_fdf
        
        if isinstance(self._model_colnames, dict):
            for model_col in self._model_colnames.values():
                data_fdf =  self.assign_column_maybe(data_fdf, model_col)
        elif isinstance(self._model_colnames, str):
            data_fdf =  self.assign_column_maybe(data_fdf, self._model_colnames)
            
        return MultiForecastDataFrame(data=data_fdf,
                                      model_colnames=self._model_colnames)
        
    def assign_column_maybe(self, data, new_column, use_zeroes=True):
        """
        Create the column if it does not exists and fill it with zeroes.
        
        :param data: The data frame to modify.
        :type: DataFrame
        :param new_columns: The name of a new column.
        :type new_columns: str
        :returns: DataFrame of data frame type with columns added if needed.
        :rtype: DataFrame
        
        """
        if not new_column in list(data.columns.values):
            if use_zeroes:
                return data.assign(**{new_column:np.zeros((len(data),))})
            else:
                return data.assign(**{new_column:np.nan})
        return data
    
    @abstractmethod
    def load_data(self, X, **kwargs):
        """
        The method used to save the data.
        
        :param data: The data frame to be saved.
        :type data: pandas.DataFrame
        
        """
        pass