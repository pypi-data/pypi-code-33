import urllib
import sqlalchemy
import pyodbc
import pandas as pd

from ftk.datasources import ForecastDataSink, SQLDataManager, DataTransformerMixin

class ForecastSQLDataSink(ForecastDataSink):
    """
    The convenience class to serialize the Time series data frames to the data base.
    
    Forecast<StorageType>DataSource classes read data from external storage.
    Forecast<StorageType>DataSink classes write data to external storage.
    They are inherited from DataTransformerMixin which implements the abstract method transform() and exact methods fit(), fit_transform(), predict() from the Transformer interface.
    SQLDataManager abstracts out the database connection capability for both ForecastSQLDataSource and ForecastSQLDataSink, which inherit from it.
    ForecastDataSource and ForecastDataSink abstract reconstruction of TimeSeriesDataFrame from the pandas.DataFrame and serialization of TimeSeriesDataFrame
    back to pandas.DataFrame of given the metadata provided by user. If the metadata were not provided the plane pandas.DataFrame
    will be loaded or saved.
    
    :param table: The name of a table to store the data
    :type table: str
    :param data_manager: The SQLDataManager object used to manipulate database.
    :type data_manager: SQLDataManager
    :param clean_df_after_sink: if True the transform will return the.
    :type clean_df_after_sink: bool
    :param run_tag: Run tag is an identifier of the pipeline run. If it is defined the table will be limited by the given run.
                    The run_tag column will be dropped from the output DataFrame.
                    Run identifier may not be longer then 255 symbols.
                    If user explicitly set run tag (in transform(), by setting it on the object or parameter on the pipeline,
                    it is used to save the data. If this parameter is not set by user, it will be set to the current time stamp
                    each time the transform() runs.
    :type run_tag: str
    
    """
    def __init__(self,
                 table,
                 sql_manager,
                 clean_df_after_sink = False,
                 add_index_as_column = False,
                 run_tag=None):
        """
        Constructor.
        
        """
        SQLDataManager.validate_name(table)
        self._clean_df_after_sink = clean_df_after_sink
        self._sql_data_manager = sql_manager
        self._table=table
        self._add_index_as_column = add_index_as_column
        super(ForecastSQLDataSink, self).__init__(clean_df_after_sink = clean_df_after_sink,
                                                  run_tag=run_tag)
    
    def save_data(self, X, **kwargs):
        """
        Save data frame to the database.
        
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
        cnxn=None
        params = urllib.parse.quote_plus(self._sql_data_manager.connection_str)
        
        cnxn = sqlalchemy.create_engine("{}+pyodbc:///?odbc_connect={}".format(self._sql_data_manager.dialect, params))
        data=X
        X = X.assign(**{DataTransformerMixin.TAG_FIELD:self.run_tag})
        if SQLDataManager.is_table_present(self._table, self._sql_data_manager.database, self._sql_data_manager.connection_str):
            pyodbc_cn = pyodbc.connect(self._sql_data_manager.connection_str)
            cursor = pyodbc_cn.cursor()
            if not self._has_column(DataTransformerMixin.TAG_FIELD):
                add_column_query = "ALTER TABLE {} \nADD ? VARCHAR({})".format(self._table, DataTransformerMixin.TAG_MAX_LENGTH)
                cursor.execute(add_column_query, (DataTransformerMixin.TAG_FIELD,))
                pyodbc_cn.commit()
                set_default_query = "UPDATE {}\nSET {}=?".format(self._table, DataTransformerMixin.TAG_FIELD)
                cursor.execute(set_default_query, (self.run_tag, ))
                pyodbc_cn.commit()
            else:
                rm_query = "DELETE FROM {} WHERE {} = ?".format(self._table, DataTransformerMixin.TAG_FIELD)
                cursor.execute(rm_query, (self.run_tag, ))
                pyodbc_cn.commit()
        X.to_sql(self._table, cnxn, if_exists='append', index=self._add_index_as_column)

        if self._clean_df_after_sink:
            data = data.iloc[0:0]
        return data
    
    def _has_column(self, column_name:str):
        """
        Return True if the given column exists, False otherwise.
        If the column name contains wrong symbol, the value error is raised.
        
        :param column_name: The name of a column.
        :type column_name: str
        :returns: True if column exists.
        :rtype: bool
        :raises: ValueError
        
        """
        SQLDataManager.validate_name(column_name)
        pyodbc_cn = pyodbc.connect(self._sql_data_manager.connection_str)
        data = pd.read_sql("SELECT TOP 1 * FROM {}".format(self._table), pyodbc_cn)
        return column_name in list(data.columns.values)
    