from ftk.datasources import DataTransformerMixin, ForecastDataSink
from azure.storage.blob.blockblobservice import BlockBlobService
from _io import StringIO

class  ForecastBlobDataSink(ForecastDataSink):
    """
    The convenience envelope for the common packages AzureBlobDataSinc
    allowing to save TimeSeriesDataFrame-s to Azure Blob.
    
    Forecast<StorageType>DataSource classes read data from external storage.
    Forecast<StorageType>DataSink classes write data to external storage.
    They are inherited from DataTransformerMixin which implements the abstract method transform() and exact methods fit(), fit_transform(), predict() from the Transformer interface.
    SQLDataManager abstracts out the database connection capability for both ForecastSQLDataSource and ForecastSQLDataSink, which inherit from it.
    ForecastDataSource and ForecastDataSink abstract reconstruction of TimeSeriesDataFrame from the pandas.DataFrame and serialization of TimeSeriesDataFrame
    back to pandas.DataFrame of given the metadata provided by user. If the metadata were not provided the plane pandas.DataFrame
    will be loaded or saved.
    
    :param container: The name of BLOB container.
    :type container: str.
    :param blob_prefix: the name of the blob i. e. the name of the file in the BLOB.
    :type blob_prefix: str.
    :param storage_account_name: the name of the storage account.
    :type storage_account_name: str.
    :param storage_account_key: the access key used for the account.
    :type storage_account_key: str.
    :param sas: Shared Access Signatures(SAS).
    :type sas: str.
    :param clean_df_after_sink: if True the transform will return the.
    :type clean_df_after_sink: bool.
    :param run_tag: Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                    The run_tag column will be dropped from the output DataFrame.
                    Run identifier may not be longer then 255 symbols.
                    If user explicitly set run tag (in transform(), by setting it on the object or parameter on the pipeline,
                    it is used to save the data. If this parameter is not set by user, it will be set to the current time stamp
                    each time the transform() runs.
    :type run_tag: str
    
    """
    def __init__(self,
                 container:str,
                 storage_account_name:str,
                 storage_account_key:str,
                 clean_df_after_sink = False,
                 run_tag=None):
        """
        Constructor.
        
        """
        self._account_name = storage_account_name
        self._account_key = storage_account_key
        self._container_name = container
        self._clean_df_after_sink = clean_df_after_sink
        super(ForecastBlobDataSink, self).__init__(clean_df_after_sink = clean_df_after_sink,
                                                   run_tag=run_tag)
        
    def save_data(self, X, **kwargs):
        """
        Save data frame to the BLOB. 
        
        :param X: the data frame which needs to be sinked to the database.
        :type X: pandas.DataFrame
        :param run_tag: Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                        The run_tag column will be dropped from the output DataFrame.
                        Run identifier may not be longer then 255 symbols.
        :type run_tag: str
        :returns: the table with data.
        :rtype: pandas.DataFrame
        :raises: ValueError
        """
        blob_service = BlockBlobService(self._account_name, self._account_key)
        pd_io = StringIO()
        if blob_service.exists(self._container_name, self.run_tag):
            blob_service.delete_blob(self._container_name, self.run_tag)
        
        X.to_csv(pd_io, index=False)   
        
        
        blob_service.create_blob_from_text(container_name=self._container_name,
                                             blob_name=self.run_tag, 
                                             text=pd_io.getvalue())
        if self._clean_df_after_sink:
            X = X.iloc[0:0]
        return X
        