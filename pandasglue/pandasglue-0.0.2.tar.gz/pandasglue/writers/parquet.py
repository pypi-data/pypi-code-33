import pyarrow as pa
from pyarrow.compat import guid
import pyarrow.parquet as pq

from .base import mkdir_if_not_exists
from ..services import s3


def write(df, fs, path, preserve_index):
    outfile = guid() + ".parquet"
    full_path = "/".join([path, outfile])
    table = pa.Table.from_pandas(df, preserve_index=preserve_index)
    with fs.open(full_path, "wb") as f:
        pq.write_table(table, f)


def write_dataset(
    df, fs, path, partition_cols, preserve_index, session_primitives, mode
):
    partition_paths = []
    dead_keys = []
    for keys, subgroup in df.groupby(partition_cols):
        subgroup = subgroup.drop(partition_cols, axis="columns")
        if not isinstance(keys, tuple):
            keys = (keys,)
        subdir = "/".join(
            [
                "{colname}={value}".format(colname=name, value=val)
                for name, val in zip(partition_cols, keys)
            ]
        )
        subtable = pa.Table.from_pandas(
            subgroup, preserve_index=preserve_index, safe=False
        )
        prefix = "/".join([path, subdir])
        if mode == "overwrite_partitions":
            dead_keys += s3.list_objects(prefix, session_primitives=session_primitives)
        mkdir_if_not_exists(fs, prefix)
        outfile = guid() + ".parquet"
        full_path = "/".join([prefix, outfile])
        with fs.open(full_path, "wb") as f:
            pq.write_table(subtable, f)
        partition_path = full_path.rpartition("/")[0] + "/"
        partition_paths.append((partition_path, keys))
    if mode == "overwrite_partitions" and dead_keys:
        bucket = path.replace("s3://", "").split("/", 1)[0]
        s3.delete_listed_objects(
            bucket, dead_keys, session_primitives=session_primitives
        )
    return partition_paths


def get_table_definition(table, partition_cols, schema, path):
    return {
        "Name": table,
        "PartitionKeys": [{"Name": x, "Type": "string"} for x in partition_cols],
        "TableType": "EXTERNAL_TABLE",
        "Parameters": {
            "classification": "parquet",
            "compressionType": "none",
            "typeOfData": "file",
        },
        "StorageDescriptor": {
            "Columns": [{"Name": x[0], "Type": x[1]} for x in schema],
            "Location": path,
            "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
            "Compressed": False,
            "NumberOfBuckets": -1,
            "SerdeInfo": {
                "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                "Parameters": {"serialization.format": "1"},
            },
            "StoredAsSubDirectories": False,
            "SortColumns": [],
            "Parameters": {
                "CrawlerSchemaDeserializerVersion": "1.0",
                "classification": "parquet",
                "compressionType": "none",
                "typeOfData": "file",
            },
        },
    }


def get_partition_definition(partition):
    return {
        u"StorageDescriptor": {
            u"InputFormat": u"org.apache.hadoop.mapred.TextInputFormat",
            u"Location": partition[0],
            u"SerdeInfo": {
                u"Parameters": {u"serialization.format": u"1"},
                u"SerializationLibrary": u"org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
            },
            u"StoredAsSubDirectories": False,
        },
        u"Values": partition[1],
    }
