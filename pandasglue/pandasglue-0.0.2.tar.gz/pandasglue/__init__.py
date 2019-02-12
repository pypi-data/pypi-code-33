from .services import base, s3  # noqa
from . import read, write


def read_glue(
    database, query, s3_output=None, region=None, key=None, secret=None, profile=None
):
    return read.read(**locals())


def write_glue(
    df,
    database,
    path,
    table=None,
    partition_cols=[],
    preserve_index=False,
    file_format="parquet",
    mode="append",
    region=None,
    key=None,
    secret=None,
    profile=None,
):
    return write.write(**locals())
