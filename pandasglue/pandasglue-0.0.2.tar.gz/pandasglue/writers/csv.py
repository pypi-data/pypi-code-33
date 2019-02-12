from pyarrow.compat import guid

from .base import mkdir_if_not_exists
from ..services import s3


def write(df, fs, path, preserve_index):
    outfile = guid() + ".csv"
    full_path = "/".join([path, outfile])
    csv_buffer = df.to_csv(None, header=False, index=preserve_index).encode()
    with fs.open(full_path, "wb") as f:
        f.write(csv_buffer)


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
        prefix = "/".join([path, subdir])
        if mode == "overwrite_partitions":
            dead_keys += s3.list_objects(prefix, session_primitives=session_primitives)
        mkdir_if_not_exists(fs, prefix)
        outfile = guid() + ".csv"
        full_path = "/".join([prefix, outfile])
        csv_buffer = subgroup.to_csv(None, header=False, index=preserve_index).encode()
        with fs.open(full_path, "wb") as f:
            f.write(csv_buffer)
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
            "classification": "csv",
            "compressionType": "none",
            "typeOfData": "file",
            "delimiter": ",",
            "columnsOrdered": "true",
            "areColumnsQuoted": "false",
        },
        "StorageDescriptor": {
            "Columns": [{"Name": x[0], "Type": x[1]} for x in schema],
            "Location": path,
            "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
            "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
            "Compressed": False,
            "NumberOfBuckets": -1,
            "SerdeInfo": {
                "Parameters": {"field.delim": ","},
                "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
            },
            "StoredAsSubDirectories": False,
            "SortColumns": [],
            "Parameters": {
                "classification": "csv",
                "compressionType": "none",
                "typeOfData": "file",
                "delimiter": ",",
                "columnsOrdered": "true",
                "areColumnsQuoted": "false",
            },
        },
    }


def get_partition_definition(partition):
    return {
        u"StorageDescriptor": {
            u"InputFormat": u"org.apache.hadoop.mapred.TextInputFormat",
            u"Location": partition[0],
            u"SerdeInfo": {
                u"Parameters": {u"field.delim": ","},
                u"SerializationLibrary": u"org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
            },
            u"StoredAsSubDirectories": False,
        },
        u"Values": partition[1],
    }
