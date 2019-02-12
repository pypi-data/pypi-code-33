import sys

from pyarrow.filesystem import _ensure_filesystem

from .exceptions import UnsupportedFileFormat, UnsupportedType, UnsupportedWriteMode
from .services.base import SessionPrimitives
from .services import s3, glue
from .writers.base import mkdir_if_not_exists
from .writers import parquet, csv


if sys.version_info.major > 2:
    string_types = str  # noqa
else:
    string_types = basestring  # noqa


def _type_pandas2athena(dtype):
    dtype = dtype.lower()
    if dtype == "int32":
        return "int"
    elif dtype == "int64":
        return "bigint"
    elif dtype == "float32":
        return "float"
    elif dtype == "float64":
        return "double"
    elif dtype == "bool":
        return "boolean"
    elif dtype == "object" and isinstance(dtype, string_types):
        return "string"
    else:
        raise UnsupportedType("Unsupported Pandas type: " + dtype)


def _build_schema(df, partition_cols, preserve_index):
    schema_built = []
    if preserve_index:
        name = str(df.index.name) if df.index.name else "index"
        df.index.name = "index"
        dtype = str(df.index.dtype)
        if name not in partition_cols:
            athena_type = _type_pandas2athena(dtype)
            schema_built.append((name, athena_type))
    for col in df.columns:
        name = str(col)
        dtype = str(df[name].dtype)
        if name not in partition_cols:
            athena_type = _type_pandas2athena(dtype)
            schema_built.append((name, athena_type))
    return schema_built


def _write_data(
    df,
    session_primitives,
    path,
    partition_cols=[],
    preserve_index=True,
    file_format="parquet",
    mode="append",
):
    """
    Write the parquet files to s3
    """
    if path[-1] == "/":
        path = path[:-1]
    fs = s3.get_fs(session_primitives=session_primitives)
    fs = _ensure_filesystem(fs)
    mkdir_if_not_exists(fs, path)
    schema = _build_schema(
        df=df, partition_cols=partition_cols, preserve_index=preserve_index
    )
    partition_paths = None
    file_format = file_format.lower()
    if partition_cols is not None and len(partition_cols) > 0:
        if file_format == "parquet":
            partition_paths = parquet.write_dataset(
                df, fs, path, partition_cols, preserve_index, session_primitives, mode
            )
        elif file_format == "csv":
            partition_paths = csv.write_dataset(
                df, fs, path, partition_cols, preserve_index, session_primitives, mode
            )
        else:
            raise UnsupportedFileFormat(file_format)
    else:
        if file_format == "parquet":
            parquet.write(df, fs, path, preserve_index)
        elif file_format == "csv":
            csv.write(df, fs, path, preserve_index)
        else:
            raise UnsupportedFileFormat(file_format)
    return schema, partition_paths


def _get_table_name(path):
    if path[-1] == "/":
        path = path[:-1]
    return path.rpartition("/")[2]


def write(
    df,
    database,
    path,
    table=None,
    partition_cols=[],
    preserve_index=True,
    file_format="parquet",
    mode="append",
    region=None,
    key=None,
    secret=None,
    profile=None,
):
    """
    Convert a given Pandas Dataframe to a Glue Parquet table
    """
    session_primitives = SessionPrimitives(
        region=None, key=None, secret=None, profile=None
    )
    if mode == "overwrite" or (mode == "overwrite_partitions" and not partition_cols):
        s3.delete_objects(path, session_primitives=session_primitives)
    elif mode not in ["overwrite_partitions", "append"]:
        raise UnsupportedWriteMode(mode)
    schema, partition_paths = _write_data(
        df=df,
        session_primitives=session_primitives,
        path=path,
        partition_cols=partition_cols,
        preserve_index=preserve_index,
        file_format=file_format,
        mode=mode,
    )
    table = table if table else _get_table_name(path)
    if mode == "overwrite":
        glue.delete_table_if_exists(
            database=database, table=table, session_primitives=session_primitives
        )
        glue.create_table(
            database=database,
            table=table,
            schema=schema,
            partition_cols=partition_cols,
            path=path,
            file_format=file_format,
            session_primitives=session_primitives,
        )
    glue.add_partitions(
        database=database,
        table=table,
        partition_paths=partition_paths,
        file_format=file_format,
        session_primitives=session_primitives,
    )
