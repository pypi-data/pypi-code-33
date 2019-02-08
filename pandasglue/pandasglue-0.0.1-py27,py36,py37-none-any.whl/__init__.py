from .read import read
from .write import write


def read_glue(
    database,
    query,
    s3_output=None,
    region=None,
    key=None,
    secret=None,
    profile_name=None,
):
    return read(
        database=database,
        query=query,
        s3_output=s3_output,
        region=region,
        key=key,
        secret=secret,
        profile_name=profile_name,
    )


def write_glue(
    df,
    database,
    path,
    table=None,
    partition_cols=[],
    preserve_index=True,
    region=None,
    key=None,
    secret=None,
    profile_name=None,
):
    return write(
        df=df,
        database=database,
        path=path,
        table=table,
        partition_cols=partition_cols,
        preserve_index=preserve_index,
        region=region,
        key=key,
        secret=secret,
        profile_name=profile_name,
    )
