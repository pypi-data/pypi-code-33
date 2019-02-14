# coding=utf-8
from __future__ import print_function

from suanpan.arguments import Int, String
from suanpan.dw.hive import HiveDataWarehouse
from suanpan.dw.odps import OdpsDataWarehouse
from suanpan.proxy import Proxy


class DataWarehouseProxy(Proxy):
    MAPPING = {"hive": HiveDataWarehouse, "odps": OdpsDataWarehouse}
    ARGUMENTS = [
        String("dw-type", default="hive"),
        String("dw-hive-host", default="localhost"),
        Int("dw-hive-port"),
        String("dw-hive-database", default="default"),
        String("dw-hive-username"),
        String("dw-hive-password"),
        String("dw-hive-auth"),
        String("dw-odps-access-id"),
        String("dw-odps-access-key"),
        String(
            "dw-odps-endpoint", default="http://service.cn.maxcompute.aliyun.com/api"
        ),
        String("dw-odps-project"),
    ]


dw = DataWarehouseProxy()
