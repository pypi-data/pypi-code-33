# coding=utf-8
from __future__ import print_function

from suanpan.datawarehouse.hive import HiveDataWarehouse
from suanpan.datawarehouse.odps import OdpsDataWarehouse
from suanpan.proxy import Proxy


class DataWarehouseProxy(Proxy):
    MAPPING = {"hive": HiveDataWarehouse, "odps": OdpsDataWarehouse}


dw = DataWarehouseProxy()
