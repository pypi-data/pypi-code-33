from unittest import TestCase
from sdhpy.pandas import get_pandas_dataframe, SdhPandas
import os


class TestBaseLoader(TestCase):
    def setUp(self):
        self.api_key = os.environ["SDH_API"]
        self.sdh = SdhPandas(store_apikey=self.api_key)
    def tearDown(self):
        pass

    def test_pandas_url(self):
        dataset = self.sdh.url(
            "http://store.smartdatahub.io/dataset/fo_hagstova_foroya_tb01010_current_accounts_summary_1998_2015/resource/2a451036-8a7f-4506-853e-26b5a000dc4a")
        self.assertIsNotNone(dataset)
        self.assertIsNotNone(dataset.data)

    def test_pandas_dynamic(self):
        dataset = self.sdh.fo_hagstova_foroya.tb01010_current_accounts_summary_1998_2015__fact_all_piped
        self.assertIsNotNone(dataset)
        self.assertIsNotNone(dataset.data)

    def test_show_tables(self):
        self.assertIsNotNone(sdh.fi_vuosien_2012_2014_data_vuoden_tarkkuudella.show_tables())

