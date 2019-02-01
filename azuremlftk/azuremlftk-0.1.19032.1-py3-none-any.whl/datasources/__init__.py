"""
ftk.datasource contains classes which allows to use Azure BLOB storage and SQL database to load and save data frames.
"""

from .data_transformer_mixin import DataTransformerMixin
from .forecast_data_source import ForecastDataSource
from .forecast_data_sink import ForecastDataSink
from .forecast_blob_data_source import ForecastBlobDataSource
from .forecast_blob_data_sink import ForecastBlobDataSink
import warnings
try:
    from .sql_data_manager import SQLDataManager
    from .forecast_sql_data_source import ForecastSQLDataSource
    from .forecast_sql_data_sink import ForecastSQLDataSink
except ImportError:
    warnings.warn('The packages required for accessing SQL server are not found. '
                  'To load data sets from SQL server please install the packages by running command:\n'
                  'pip install sqlparse pyodbc sqlalchemy')