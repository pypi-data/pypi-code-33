import unittest

from pyspark.sql import SparkSession
from manifestare.core import SparkDataFrameManifesto
from test.testbuilders import SparkDataFrameTestBuilder

class TestPandasDataFrameManifesto(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.spark = SparkSession.builder.appName('manifestare-test').getOrCreate()

    @classmethod
    def tearDownClass(self):
        if (self.spark):
            self.spark.stop()

    def test_pass_when_an_existent_column_is_provided(self):
        df = SparkDataFrameTestBuilder(self.spark).buildSimpleDataFrame()

        try:
            SparkDataFrameManifesto().describeThat(df).doesHaveColumn('x')
        except AssertionError:
            self.fail()

    def test_fail_when_a_non_existent_column_is_provided(self):
        df = SparkDataFrameTestBuilder(self.spark).buildSimpleDataFrame()

        try:
            SparkDataFrameManifesto().describeThat(df).doesHaveColumn('nonexistent')
        except AssertionError:
            return

        self.fail()

    def test_fail_when_None_is_provided_as_column(self):
        df = SparkDataFrameTestBuilder(self.spark).buildSimpleDataFrame()

        try:
            SparkDataFrameManifesto().describeThat(df).doesHaveColumn(None)
        except AssertionError:
            return

        self.fail()
