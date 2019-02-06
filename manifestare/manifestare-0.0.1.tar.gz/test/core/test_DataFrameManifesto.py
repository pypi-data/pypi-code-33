import unittest

from pandas import DataFrame as PandasDataFrame
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import SparkSession

from manifestare.core import DataFrameManifesto

from test import PandasDataFrameTestBuilder
from test import SparkDataFrameTestBuilder

class TestDataFrameManifesto(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.spark = SparkSession.builder.appName('manifestare-test').getOrCreate()

    @classmethod
    def tearDownClass(self):
        if (self.spark):
            self.spark.stop()

    def test_creates_a_new_DataFrameManifesto(self):
        manifesto = DataFrameManifesto()

        assert manifesto != None
        assert isinstance(manifesto, DataFrameManifesto)

    def test_a_new_DataFrameManifesto_can_describe_a_PandasDataFrame(self):
        dataframe = PandasDataFrameTestBuilder().buildEmptyDataFrame()

        manifesto = DataFrameManifesto()
        manifesto.describeThat(dataframe)

        assert isinstance(manifesto.df, PandasDataFrame)

    def test_a_new_DataFrameManifesto_can_describe_a_SparkDataFrame(self):
        dataframe = SparkDataFrameTestBuilder(self.spark).buildEmptyDataFrame()

        manifesto = DataFrameManifesto()
        manifesto.describeThat(dataframe)

        assert isinstance(manifesto, DataFrameManifesto)
        assert isinstance(manifesto.df, SparkDataFrame)

    def test_describeThat_returns_a_DataFrameManifesto(self):
        dataframe = PandasDataFrameTestBuilder().buildEmptyDataFrame()

        manifesto = DataFrameManifesto().describeThat(dataframe)

        assert manifesto != None
        assert isinstance(manifesto, DataFrameManifesto)

    def test_end_returns_None(self):
        manifesto = DataFrameManifesto().end()

        assert manifesto == None
        assert not isinstance(manifesto, DataFrameManifesto)
