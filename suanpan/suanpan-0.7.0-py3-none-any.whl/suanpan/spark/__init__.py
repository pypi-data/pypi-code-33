# coding=utf-8
from __future__ import print_function

from contextlib import contextmanager

from pyspark.sql import SparkSession

from suanpan import Context
from suanpan.components import Component


class SparkComponent(Component):
    @contextmanager
    def context(self, args):
        spark = (
            SparkSession.builder.appName(self.runFunc.__name__)
            .enableHiveSupport()
            .getOrCreate()
        )
        yield Context(spark=spark)
        spark.stop()
