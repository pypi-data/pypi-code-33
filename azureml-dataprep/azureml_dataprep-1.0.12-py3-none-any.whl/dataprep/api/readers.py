# Copyright (c) Microsoft Corporation. All rights reserved.
from .builders import InferenceArguments, FileFormatBuilder
from .dataflow import Dataflow, FilePath, DatabaseSource
from .datasources import FileDataSource, MSSQLDataSource
from ._datastore_helper import Datastore, datastore_to_dataflow, NotSupportedDatastoreTypeError
from .engineapi.typedefinitions import PromoteHeadersMode, SkipMode, FileEncoding
from .engineapi.api import get_engine_api
from .parseproperties import ParseParquetProperties
from ._archiveoption import ArchiveOptions
from typing import TypeVar, List
import pandas as pd
import warnings


def _default_skip_mode(skip_mode: SkipMode, skip_rows: int) -> SkipMode:
    return SkipMode.UNGROUPED if skip_rows > 0 and skip_mode == SkipMode.NONE else skip_mode


def read_csv(path: FilePath,
             separator: str = ',',
             header: PromoteHeadersMode = PromoteHeadersMode.CONSTANTGROUPED,
             encoding: FileEncoding = FileEncoding.UTF8,
             quoting: bool = False,
             inference_arguments: InferenceArguments = None,
             skip_rows: int = 0,
             skip_mode: SkipMode = SkipMode.NONE,
             comment: str = None,
             include_path: bool = False,
             archive_options: ArchiveOptions = None) -> Dataflow:
    """
    Creates a new Dataflow with the operations required to read and parse CSV data.

    :param path: The file(s) to load and parse.
    :param separator: The separator to use to split columns.
    :param header: How to determine column headers.
    :param encoding: The encoding of the files being read.
    :param quoting: Whether to handle new line characters within quotes. This option will impact performance.
    :param inference_arguments: Arguments that determine how data types are inferred.
    :param skip_rows: How many rows to skip.
    :param skip_mode: The mode in which rows are skipped.
    :param comment: Character used to indicate a line is a comment instead of data in the files being read.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :param archive_options: Options for archive file, including archive type and entry glob pattern.
    :return: A new Dataflow.
    """
    skip_mode = _default_skip_mode(skip_mode, skip_rows)
    df = Dataflow._path_to_get_files_block(path, archive_options)
    df = df.parse_delimited(separator, header, encoding, quoting, skip_rows, skip_mode, comment)

    if inference_arguments is not None:
        column_types_builder = df.builders.set_column_types()
        column_types_builder.learn(inference_arguments)
        df = column_types_builder.to_dataflow()

    if not include_path:
        df = df.drop_columns(['Path'])

    return df


def read_fwf(path: FilePath,
             offsets: List[int],
             header: PromoteHeadersMode = PromoteHeadersMode.CONSTANTGROUPED,
             encoding: FileEncoding = FileEncoding.UTF8,
             inference_arguments: InferenceArguments = None,
             skip_rows: int = 0,
             skip_mode: SkipMode = SkipMode.NONE,
             include_path: bool = False) -> Dataflow:
    """
    Creates a new Dataflow with the operations required to read and parse fixed-width data.

    :param path: The file(s) to load and parse.
    :param offsets: The offsets at which to split columns. The first column is always assumed to start at offset 0.
    :param header: How to determine column headers.
    :param encoding: The encoding of the files being read.
    :param inference_arguments: Arguments that determine how data types are inferred.
    :param skip_rows: How many rows to skip.
    :param skip_mode: The mode in which rows are skipped.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :return: A new Dataflow.
    """
    skip_mode = _default_skip_mode(skip_mode, skip_rows)
    df = Dataflow._path_to_get_files_block(path)
    df = df.parse_fwf(offsets, header, encoding, skip_rows, skip_mode)

    if inference_arguments is not None:
        column_types_builder = df.builders.set_column_types()
        column_types_builder.learn(inference_arguments)
        df = column_types_builder.to_dataflow()

    if not include_path:
        df = df.drop_columns(['Path'])

    return df


def read_excel(path: FilePath,
               sheet_name: str = None,
               use_column_headers: bool = False,
               inference_arguments: InferenceArguments = None,
               skip_rows: int = 0,
               include_path: bool = False) -> Dataflow:
    """
    Creates a new Dataflow with the operations required to read Excel files.

    :param path: The file(s) to read.
    :param sheet_name: The name of the sheet to load.
    :param use_column_headers: Whether to use the first row as column headers.
    :param inference_arguments: Arguments that determine how data types are inferred.
    :param skip_rows: How many rows to skip.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :return: A new Dataflow.
    """
    df = Dataflow._path_to_get_files_block(path)
    df = df.read_excel(sheet_name, use_column_headers, skip_rows)

    if inference_arguments is not None:
        column_types_builder = df.builders.set_column_types()
        column_types_builder.learn(inference_arguments)
        df = column_types_builder.to_dataflow()

    if not include_path:
        df = df.drop_columns(['Path'])

    return df


def read_lines(path: FilePath,
               header: PromoteHeadersMode = PromoteHeadersMode.NONE,
               encoding: FileEncoding = FileEncoding.UTF8,
               skip_rows: int = 0,
               skip_mode: SkipMode = SkipMode.NONE,
               comment: str = None,
               include_path: bool = False) -> Dataflow:
    """
    Creates a new Dataflow with the operations required to read text files and split them into lines.

    :param path: The file(s) to read.
    :param header: How to determine column headers.
    :param encoding: The encoding of the files being read.
    :param skip_rows: How many rows to skip.
    :param skip_mode: The mode in which rows are skipped.
    :param comment: Character used to indicate a line is a comment instead of data in the files being read.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :return: A new Dataflow.
    """
    skip_mode = _default_skip_mode(skip_mode, skip_rows)
    df = Dataflow._path_to_get_files_block(path)
    df = df.parse_lines(header, encoding, skip_rows, skip_mode, comment)

    if not include_path:
        df = df.drop_columns(['Path'])

    return df


def detect_file_format(path: FilePath) -> FileFormatBuilder:
    """
    Analyzes the file(s) at the specified path and attempts to determine the type of file and the arguments required
        to read and parse it. The result is a FileFormatBuilder which contains the results of the analysis. This builder
        can be modified and used as the input to a new Dataflow.

    :param path: The file(s) to analyze.
    :return: A FileFormatBuilder.
    """
    df = Dataflow._path_to_get_files_block(path)

    # File Format Detection
    ffb = df.builders.detect_file_format()
    ffb.learn()
    return ffb


def smart_read_file(path: FilePath, include_path: bool = False) -> Dataflow:
    """
    (Deprecated. Use auto_read_file instead.)

    Analyzes the file(s) at the specified path and returns a new Dataflow containing the operations required to
        read and parse them. The type of the file and the arguments required to read it are inferred automatically.

    :param path: The file(s) to read.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :return: A new Dataflow.
    """
    warnings.warn('Function smart_read_file is deprecated. Use auto_read_file instead.', category=DeprecationWarning, stacklevel=2)
    return auto_read_file(path, include_path)


def auto_read_file(path: FilePath, include_path: bool = False) -> Dataflow:
    """
    Analyzes the file(s) at the specified path and returns a new Dataflow containing the operations required to
        read and parse them. The type of the file and the arguments required to read it are inferred automatically.

    :param path: The file(s) to read.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :return: A new Dataflow.
    """
    df = Dataflow._path_to_get_files_block(path)

    # File Format Detection
    ffb = df.builders.detect_file_format()
    ffb.learn()
    df = ffb.to_dataflow(include_path=include_path)

    # Type Inference, except for parquet
    if type(ffb.file_format) != ParseParquetProperties:
        column_types_builder = df.builders.set_column_types()
        column_types_builder.learn()
        # in case any date ambiguity skip setting column type to let user address it separately.
        column_types_builder.ambiguous_date_conversions_drop()
        df = column_types_builder.to_dataflow()

    return df


def read_sql(data_source: DatabaseSource, query: str) -> Dataflow:
    """
    Creates a new Dataflow that can read data from a Microsoft SQL or Azure SQL database by executing the query specified.

    :param data_source: The details of the Microsoft SQL or Azure SQL database.
    :param query: The query to execute to read data.
    :return: A new Dataflow.
    """
    try:
        from azureml.data.abstract_datastore import AbstractDatastore
        from azureml.data.azure_sql_database_datastore import AzureSqlDatabaseDatastore
        from azureml.data.datapath import DataPath

        if isinstance(data_source, AzureSqlDatabaseDatastore):
            return datastore_to_dataflow(DataPath(data_source, query))
        if isinstance(data_source, AbstractDatastore):
            raise NotSupportedDatastoreTypeError(data_source)
    except ImportError:
        pass
    df = Dataflow(get_engine_api())
    df = df.read_sql(data_source, query)

    return df


def read_parquet_file(path: FilePath, include_path: bool = False) -> Dataflow:
    """
    Creates a new Dataflow with the operations required to read Parquet files.

    :param path: The file(s) to be read.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :return: A new Dataflow.
    """
    df = Dataflow._path_to_get_files_block(path)
    df = df.read_parquet_file()

    if not include_path:
        df = df.drop_columns(['Path'])

    return df


def read_parquet_dataset(path: FilePath, include_path: bool = False) -> Dataflow:
    """
    Creates a new Dataflow with the operations required to read Parquet Datasets.

    .. remarks::

        A Parquet Dataset is different from a Parquet file in that it could be a Folder containing a number of Parquet
        Files. It could also have a hierarchical structure that partitions the data by the value of a column. These more
        complex forms of Parquet data are produced commonly by Spark/HIVE.
        read_parquet_dataset will read these more complex datasets using pyarrow which handle complex Parquet layouts
        well. It will also handle single Parquet files, or folders full of only single Parquet files, though these are
        better read using read_parquet_file as it doesn't use pyarrow for reading and should be significantly faster
        than use pyarrow.

    :param path: The path(s) to be read.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :return: A new Dataflow.
    """
    datasource = None
    if isinstance(path, str):
        datasource = FileDataSource.datasource_from_str(path)
    elif isinstance(path, FileDataSource):
        datasource = path
    else:
        raise RuntimeError("{} is not supported by read_parquet_dataset")
    df = Dataflow.read_parquet_dataset(datasource)

    if not include_path:
        df = df.drop_columns(['Path'])

    return df


def read_json(path: FilePath,
              encoding: FileEncoding = FileEncoding.UTF8,
              flatten_nested_arrays: bool = False,
              include_path: bool = False) -> Dataflow:
    """
    Creates a new Dataflow with the operations required to read JSON files.

    :param path: The file(s) to be read.
    :param encoding: The encoding of the files being read.
    :param flatten_nested_arrays: Property controlling program's handling of nested arrays.
    :param include_path: Whether to include a column containing the path from which the data was read.
    :return: A new Dataflow.
    """
    df = Dataflow._path_to_get_files_block(path)

    # Json format detection
    builder = df.builders.extract_table_from_json()
    builder.encoding = encoding
    builder.flatten_nested_arrays = flatten_nested_arrays
    builder.learn()
    df = builder.to_dataflow()

    if not include_path:
        df = df.drop_columns(['Path'])

    return df


def read_pandas_dataframe(df: 'pd.DataFrame', temp_folder: str) -> Dataflow:
    """
    Creates a new Dataflow based on the contents of a given pandas DataFrame.

    .. remarks::

        The contents of 'df' will be written to 'temp_folder' as a DataPrep DataSet. This folder
        must be accessible both from the calling script and from any environment where the
        Dataflow is executed.

    :param df: pandas DataFrame to be parsed and cached at 'temp_folder'.
    :param temp_folder: path to folder that 'df' contents will be written to.
    :return: Dataflow that uses the contents of cache_path as its datasource.
    """
    if temp_folder is None:
        raise ValueError('temp_folder must be provided.')

    import os
    import numpy as np
    from azureml.dataprep import native
    new_schema = df.columns.tolist()
    new_values = []
    # Handle Categorical typed columns. Categorical is a pandas type not a numpy type and azureml-dataprep-native can't
    # handle it. This is temporary pending improvments to native that can handle Categoricals, vso: 246011
    for column_name in new_schema:
        if pd.api.types.is_categorical_dtype(df[column_name]):
            new_values.append(np.asarray(df[column_name]))
        else:
            new_values.append(df[column_name].values)
    # new_values = [df[column_name].values for column_name in new_schema]

    abs_cache_path = os.path.abspath(temp_folder)
    os.makedirs(abs_cache_path, exist_ok=True)
    if (len(os.listdir(abs_cache_path)) > 0):
        raise ValueError('temp_folder must be empty.')

    # This will write out part files to cache_path.
    native.preppy_files_from_ndarrays(new_values, new_schema, abs_cache_path)
    dflow = Dataflow.get_files(FileDataSource.datasource_from_str(os.path.join(abs_cache_path, 'part-*')))
    dflow = dflow.add_step('Microsoft.DPrep.ParseDataSetBlock', {})
    return dflow.drop_columns(['Path'])
