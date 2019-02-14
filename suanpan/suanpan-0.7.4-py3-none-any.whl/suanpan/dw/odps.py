# coding=utf-8
from __future__ import print_function

from odps import ODPS
from odps.df import DataFrame

from suanpan.log import logger


class OdpsDataWarehouse(object):
    DEFAULT_ODPS_PROJECT_NAME = "None"

    DTYPE_SQLTYPE_MAPPING = {
        "int8": "tinyint",
        "int16": "smallint",
        "int32": "int",
        "int64": "bigint",
        "float32": "float",
        "float64": "double",
        "class": "string",
        "datetime": "timestamp",
    }

    def __init__(
        self, odpsAccessId, odpsAccessKey, odpsEndpoint, odpsProject, **kwargs
    ):
        self.odpsAccessId = odpsAccessId
        self.odpsAccessKey = odpsAccessKey
        self.odpsEndpoint = odpsEndpoint
        self.odpsProject = odpsProject

        self._connection = self.connect()

    def connect(self):
        connection = ODPS(
            access_id=self.odpsAccessId,
            secret_access_key=self.odpsAccessKey,
            endpoint=self.odpsEndpoint,
            project=self.odpsProject,
        )
        return connection

    def testConnection(self, connection):
        connection.execute_sql("select current_timestamp()")
        logger.info("Odps connected...")

    def readTable(self, table, partition=None, database=DEFAULT_ODPS_PROJECT_NAME):
        df = (
            DataFrame(self._connection.get_table(table).get_partition(partition))
            if partition
            else DataFrame(self._connection.get_table(table))
        )
        return df

    def writeTable(
        self,
        table,
        data,
        partition=None,
        database=DEFAULT_ODPS_PROJECT_NAME,
        overwrite=True,
    ):
        if not isinstance(data, DataFrame):
            data = DataFrame(data)

        if partition:
            data.persist(
                table,
                partition=partition,
                drop_partition=overwrite,
                create_partition=True,
                odps=self._connection,
            )
        else:
            data.persist(
                table,
                partition=partition,
                drop_table=overwrite,
                create_table=True,
                odps=self._connection,
            )

    def createTable(self, table, columns):
        self.execute(
            u"create table if not exists {table} ({columns})".format(
                table=table,
                columns=u",".join(
                    [
                        u"{} {}".format(column["name"], column["type"])
                        for column in columns
                    ]
                ),
            )
        )

    def dropTable(self, connection, table):
        connection.delete_table(table)

    def execute(self, sql):
        try:
            self._connection.execute_sql(sql)
        except Exception as e:
            logger.error("SQL: {}".format(sql))
            raise e

    def getColumns(self, data):
        return [
            {"name": name.split(".")[-1], "type": self.toSqlType(dtype)}
            for name, dtype in data.dtypes.items()
        ]

    def toSqlType(self, dtype):
        typeName = self.shortenDatetimeType(dtype.name)
        return self.DTYPE_SQLTYPE_MAPPING.get(typeName, "string")

    def shortenDatetimeType(self, typeName):
        datatimeType = "datetime"
        return datatimeType if typeName.startswith(datatimeType) else typeName
