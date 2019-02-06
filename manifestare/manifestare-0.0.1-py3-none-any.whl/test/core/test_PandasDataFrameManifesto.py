import unittest

from manifestare.core import PandasDataFrameManifesto

from test import PandasDataFrameTestBuilder

class TestPandasDataFrameManifesto(unittest.TestCase):

    def test_pass_when_an_existent_column_is_provided(self):
        df = PandasDataFrameTestBuilder().buildSimpleDataFrame()

        try:
            PandasDataFrameManifesto().describeThat(df).doesHaveColumn('x')
        except AssertionError:
            self.fail()

    def test_fail_when_a_non_existent_column_is_provided(self):
        df = PandasDataFrameTestBuilder().buildSimpleDataFrame()

        try:
            PandasDataFrameManifesto().describeThat(df).doesHaveColumn('nonexistent')
        except AssertionError:
            return

        self.fail()

    def test_fail_when_None_is_provided_as_column(self):
        df = PandasDataFrameTestBuilder().buildSimpleDataFrame()

        try:
            PandasDataFrameManifesto().describeThat(df).doesHaveColumn(None)
        except AssertionError:
            return

        self.fail()
