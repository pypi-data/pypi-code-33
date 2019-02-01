import pandas as pd
import numpy as np

from ftk.datasources import ForecastDataSource, DataTransformerMixin
from azure.storage.blob.blockblobservice import BlockBlobService
from _io import StringIO

class ForecastBlobDataSource(ForecastDataSource):
    """
    
    There are two ways to authenticate on the service: using SAS (Shared Access Signatures) token and
    usinfg account name and key.
    The SAS method is highly recommended because it allows to share the content without sharing keys.
    If there no key or account name is provided and there is no SAS the Value error rises.
    
    Forecast<StorageType>DataSource classes read data from external storage.
    Forecast<StorageType>DataSink classes write data to external storage.
    They are inherited from DataTransformerMixin which implements the abstract method transform() and exact methods fit(), fit_transform(), predict() from the Transformer interface.
    SQLDataManager abstracts out the database connection capability for both ForecastSQLDataSource and ForecastSQLDataSink, which inherit from it.
    ForecastDataSource and ForecastDataSink abstract reconstruction of TimeSeriesDataFrame from the pandas.DataFrame and serialization of TimeSeriesDataFrame
    back to pandas.DataFrame of given the metadata provided by user. If the metadata were not provided the plane pandas.DataFrame
    will be loaded or saved.
     
    
    
    :param container: The name of BLOB container.
    :type container: str.
    :param time_colname: The time_colname to create TimeSeriesDataFrame.
    :type time_colname: str.
    :param storage_account_name: the name of the storage account.
    :type storage_account_name: str.
    :param storage_account_key: the access key used for the account.
    :type storage_account_key: str.
    :param sas: Shared Access Signatures(SAS).
    :type sas: str.
    :param grain_colnames: The grain colnames to create TimeSeriesDataFrame.
    :type grain_colnames: list.
    :param ts_value_colname: The Time series value column name.
    :type ts_value_colname: str.
    :param origin_time_colname: The column name for the origin time to create TimeSeriesDataFrame. 
    :type origin_time_colname: str.
    :param pred_point: The point forecast column name. The metadata fore ForecastDataFrame. 
    :type pred_point: str.
    :param pred_dist: The distribution forecast column name. The metadata fore ForecastDataFrame.
    :type pred_dist: str.
    :param model_colnames: The name of model colname. The metadata fore MultiForecastDataFrame.
    :type model_colnames: list.
    :param deduplicate: Deduplicate the index.
    :type deduplicate: bool.
    :param run_tag: The pipeline run identifier to be used retrieve data only matching the tag.
                    If run_tag is None, all records will be returned.
                    Run identifier may not be longer then 255 symbols.
    :type run_tag: str
    :rises: ValueError.
    """
    def __init__(self,                       
                 container:str,
                 time_colname:str=None,
                 storage_account_name:str = None,
                 storage_account_key:str = None,
                 sas:str = None,
                 grain_colnames=None,
                 ts_value_colname=None,
                 origin_time_colname=None,
                 pred_point=None,
                 pred_dist=None,
                 model_colnames=None,
                 run_tag = None,
                 deduplicate=False):
        """Constructor.
        
        """
        if (storage_account_key is None or storage_account_name is None) and sas is None:
           raise ValueError("Please provide SAS or storage account name and key to authenticate on the BLOB service.")
        self._account_name = storage_account_name
        self._account_key = storage_account_key
        self._container_name = container
        self._sas = sas
        super(ForecastBlobDataSource, self).__init__(time_colname = time_colname,
                                                     grain_colnames = grain_colnames,
                                                     ts_value_colname = ts_value_colname,
                                                     origin_time_colname = origin_time_colname,
                                                     pred_point = pred_point,
                                                     pred_dist = pred_dist,
                                                     model_colnames = model_colnames,
                                                     deduplicate=deduplicate,
                                                     run_tag=run_tag
                                                    )
        
    def load_data(self, X=None, **kwargs):    
        """
        Retrieve the data from the SQL database.
        If X is connection info, then ignore connection string
        provided in constructor and use that. Blob discovery is forbidden if we use SAS.
        To use transform without run_tag, use storage_account_key instead. 
        
        :param X: Conntection string.
        :type X: str
        :param run_tag: Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                        The run_tag column will be dropped from the output DataFrame.
                        Run identifier may not be longer then 255 symbols.
        :type run_tag: str.
        :returns: the table with data.
        :rtype: pandas.DataFrame
        :raises: ValueError
        """
        DataTransformerMixin.check_run_tag(**kwargs)
        data = None
        if self._account_key is None and kwargs.get(DataTransformerMixin.TAG_VAR) is None:
            raise ValueError('Blob discovery is not allowed with SAS.' 
                             'Use storage account key to authenticate instead or provide the run_tag value.')
        blob_service = BlockBlobService(self._account_name, self._account_key, sas_token=self._sas)
        if kwargs.get(DataTransformerMixin.TAG_VAR) is None: #Go over all BLOB storages and concatenate to one data frame.
            accum = []
            for blob_model in blob_service.list_blobs(container_name=self._container_name):
                blob = blob_service.get_blob_to_text(container_name=self._container_name,
                                                     blob_name=blob_model.name)
                accum.append(pd.read_csv(StringIO(blob.content)))
            data = pd.concat(accum).reset_index(drop=True)
        else: #take only one blob.
            blob = blob_service.get_blob_to_text(container_name=self._container_name,
                                                 blob_name=kwargs.get(DataTransformerMixin.TAG_VAR))
            data = pd.read_csv(StringIO(blob.content))
        return data
    