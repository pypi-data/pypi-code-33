import unittest
import logging
from os import path
from datetime import datetime
import pandas as pd
from dativa.analyzer import DataFrameAnalyzer

logger = logging.getLogger("dativa.analyzer.tests")


class FileAnalyserTests(unittest.TestCase):

    def setUp(self):
        self.base_path = "{0}/test-data/analyzer/".format(
            path.dirname(path.abspath(__file__)))
        super(FileAnalyserTests, self).setUp()

    def test_exception(self):
        logger.debug("testing exception")
        df = pd.read_csv(self.base_path + "decimal_places.csv")

        has_exception = False
        try:
            DataFrameAnalyzer(df)
        except Exception:
            has_exception = True
        self.assertTrue(has_exception)

    def test_decimal_places(self):
        logger.debug("testing decimal places file...")
        df = pd.read_csv(self.base_path +
                         "decimal_places.csv", dtype=pd.np.str)
        analyser = DataFrameAnalyzer(df)
        columns = analyser.columns

        self.assertEqual(columns[0].name, "Number")
        self.assertEqual(columns[0].type, "number")
        self.assertEqual(columns[0].min, -10)
        self.assertEqual(columns[0].max, 10)
        self.assertEqual(columns[0].decimal_places, 1)

        logger.debug("testing no decimal places file...")
        df = pd.read_csv(self.base_path +
                         "no_decimal_places.csv", dtype=pd.np.str)
        analyser = DataFrameAnalyzer(df)
        columns = analyser.columns

        self.assertEqual(columns[0].name, "Number")
        self.assertEqual(columns[0].type, "number")
        self.assertEqual(columns[0].min, 1)
        self.assertEqual(columns[0].max, 10)
        self.assertEqual(columns[0].decimal_places, 0)

    def test_epg_file(self):
        logger.debug("testing EPG file...")
        df = pd.read_csv(self.base_path + "epg-jan-2017.csv", dtype=pd.np.str)
        analyser = DataFrameAnalyzer(df)
        columns = analyser.columns

        self.assertEqual(columns[0].name, "station_name")
        self.assertEqual(columns[0].type, "string")
        self.assertEqual(columns[0].min, 1)
        self.assertEqual(columns[0].max, 100)
        self.assertEqual(columns[0].number_references, 213)

        self.assertEqual(columns[1].name, "airdate")
        self.assertEqual(columns[1].type, "date")
        self.assertEqual(columns[1].date_format, "%Y-%m-%d %H:%M:%S")
        self.assertEqual(columns[1].min, datetime.strptime(
            "2017-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(datetime.strptime(
            "2017-02-28 23:59:59.999999", "%Y-%m-%d %H:%M:%S.%f"), columns[1].max)

        self.assertEqual(columns[2].name, "title")
        self.assertEqual(columns[2].type, "string")
        self.assertEqual(columns[2].min, 1)
        self.assertEqual(columns[2].max, 100)

        self.assertEqual(columns[3].name, "epi_num")
        self.assertEqual(columns[3].type, "string")
        self.assertEqual(columns[3].min, 1)
        self.assertGreater(columns[3].max, 9)

        self.assertEqual(columns[4].name, "epi_title")
        self.assertEqual(columns[4].type, "string")
        self.assertEqual(columns[4].min, 1)
        self.assertGreater(columns[4].max, 99)

        self.assertEqual(columns[5].name, "genre")
        self.assertEqual(columns[5].type, "string")
        self.assertGreater(columns[5].min, -1)
        self.assertEqual(columns[5].max, 100)

        self.assertEqual(columns[6].name, "year")
        self.assertEqual(columns[6].type, "number")
        self.assertEqual(columns[6].decimal_places, 0)
        self.assertEqual(columns[6].min, 1000)
        self.assertEqual(columns[6].max, 3000)

        self.assertEqual(columns[7].name, "language")
        self.assertEqual(columns[7].type, "string")
        self.assertEqual(columns[7].min, 0)
        self.assertEqual(columns[7].max, 10)
        self.assertEqual(columns[7].number_references, 2)

        self.assertEqual(columns[8].name, "country_name")
        self.assertEqual(columns[8].type, "string")
        self.assertEqual(columns[8].min, 0)
        self.assertEqual(columns[8].max, 20)
        self.assertEqual(columns[8].number_references, 87)

        self.assertEqual(analyser.get_unique_columns(
            0.95, 5), ['station_name', 'airdate'])

    def test_vod_file(self):
        logger.debug("testing VOD file...")
        df = pd.read_csv(self.base_path + "vod-jun-2017.csv", dtype=pd.np.str)
        analyser = DataFrameAnalyzer(df)

    def test_date_hour_month(self):
        logger.debug("testing date hour month places file...")
        df = pd.read_csv(self.base_path +
                         "dates_hour_month.csv", dtype=pd.np.str)
        analyser = DataFrameAnalyzer(df)
        columns = analyser.columns

        self.assertEqual(columns[0].name, "hours")
        self.assertEqual(columns[0].type, "date")
        self.assertEqual(columns[0].min, datetime.strptime(
            '2017-12-01 12:00:00', "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(columns[0].max, datetime.strptime(
            '2017-12-01 12:59:59.999999', "%Y-%m-%d %H:%M:%S.%f"))

        self.assertEqual(columns[1].name, "days")
        self.assertEqual(columns[1].type, "date")
        self.assertEqual(columns[1].min, datetime.strptime(
            '2017-12-01 00:00:00', "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(columns[1].max, datetime.strptime(
            '2017-12-31 23:59:59.999999', "%Y-%m-%d %H:%M:%S.%f"))
