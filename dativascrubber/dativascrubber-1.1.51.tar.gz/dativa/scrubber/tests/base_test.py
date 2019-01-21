# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

import unittest
import logging
# import json
from os import path, remove
import pandas as pd
from dativa.tools.pandas import CSVHandler
from dativa.scrubber import Scrubber

logger = logging.getLogger("dativa.scrubber.tests")


class _BaseTest(unittest.TestCase):
    ScrubberClass = Scrubber

    def setUp(self):
        self.base_path = "{0}/test-data/".format(
            path.dirname(path.abspath(__file__)))
        super(_BaseTest, self).setUp()

    def _compare_df_to_file(self, csv, df, file):
        """

        :param csv: an instance of a CSVHandler class
        :param df: the dataframe to compare
        :param file: the file to compare
        :return: raises an exception if they not the same
        """

        # save and reload the df to overcome differences in file handling
        # between platforms
        temp_file = "temp.csv"
        csv.save_df(df, temp_file)
        test_df = csv.load_df(temp_file)
        remove(path.join(csv.base_path, temp_file))

        clean_df = csv.load_df(file)
        pd.testing.assert_frame_equal(clean_df, test_df)

    def _test_filter_actual(self,
                            dirty_file,
                            clean_file,
                            config,
                            expected_report,
                            csv_encoding,
                            csv_delimiter,
                            csv_header,
                            csv_skiprows,
                            csv_quotechar,
                            report_writer,
                            profile,
                            expected_error,
                            expected_df_dict,
                            force_dtype):

        csv = CSVHandler(csv_encoding=csv_encoding,
                         csv_delimiter=csv_delimiter,
                         csv_header=csv_header,
                         csv_skiprows=csv_skiprows,
                         csv_quotechar=csv_quotechar,
                         base_path=self.base_path,
                         force_dtype=str)

        scrubber = self.ScrubberClass(report_writer, profile)

        dataframe_dict = {}
        for file in scrubber.get_files_from_config(config):
            dataframe_dict[file] = csv.get_dataframe(file, force_dtype=pd.np.str)

        df = csv.get_dataframe(dirty_file, force_dtype=force_dtype)
        report = scrubber.run(df, config, dataframe_dict)

        # -------------------------------------------------------------------------
        # UNCOMMENT THIS CODE TO ASSIST IN GETTING THE REPORT OBJECTS FOR NEW TESTS
        # -------------------------------------------------------------------------
        # print(",")
        # print("report = [")
        # import numpy as np
        # np.set_printoptions(threshold=np.nan)
        # for r in report:
        #     print("{")
        #     print("""
        #     'field': '{0}',
        #            'rule': '{1}',
        #            'number_records': {2},
        #            'category': '{3}',
        #            'description': '{4}',
        #            'df': {5},
        #            """.format(r.field, r.rule, r.number_records, r.category, r.description,
        #                       repr(r.df.values).replace("array(", "").replace(", dtype=object)", "").replace(
        #                           "dtype=object),", "").replace("Timestamp", "_to_time")).replace("nan", "None"))
        #     print("},")
        # print("]")
        # -------------------------------------------------------------------------

        if expected_report is not None:

            self.assertEqual(len(report), len(expected_report))
            for i in range(0, len(report)):
                self.assertEqual(report[i].field, expected_report[i]["field"])
                self.assertEqual(report[i].rule, expected_report[i]["rule"])
                self.assertEqual(report[i].number_records, expected_report[i]["number_records"])
                self.assertEqual(report[i].category, expected_report[i]["category"])
                self.assertEqual(report[i].description, expected_report[i]["description"])
                pd.np.array_equal(report[i].df.values, expected_report[i]["df"], )

        self._compare_df_to_file(csv, df, clean_file)

        if expected_df_dict is not None:
            for file in expected_df_dict:
                try:
                    expected_df = csv.get_dataframe(expected_df_dict[file])
                    actual_df = dataframe_dict[file]
                    pd.testing.assert_frame_equal(expected_df, actual_df)
                except TypeError:
                    expected_df = csv.get_dataframe(file)
                    actual_df = dataframe_dict[file]
                    pd.testing.assert_frame_equal(expected_df, actual_df)

    def _test_filter(self,
                     dirty_file,
                     clean_file,
                     config,
                     report=None,
                     csv_encoding="UTF-8",
                     csv_delimiter=",",
                     csv_header=0,
                     csv_skiprows=0,
                     csv_quotechar='"',
                     report_writer=None,
                     profile=None,
                     expected_error=None,
                     expected_df_dict=None,
                     force_dtype=None):

        logger.debug("testing {0}".format(dirty_file))

        if expected_error is None:
            val = self._test_filter_actual(dirty_file,
                                           clean_file,
                                           config,
                                           report,
                                           csv_encoding,
                                           csv_delimiter,
                                           csv_header,
                                           csv_skiprows,
                                           csv_quotechar,
                                           report_writer,
                                           profile,
                                           expected_error,
                                           force_dtype=force_dtype,
                                           expected_df_dict=expected_df_dict)

            if report is None:
                raise ValueError("Report not set for test")

            return val

        with self.assertRaises(expected_error):
            return self._test_filter_actual(dirty_file,
                                            clean_file,
                                            config,
                                            report,
                                            csv_encoding,
                                            csv_delimiter,
                                            csv_header,
                                            csv_skiprows,
                                            csv_quotechar,
                                            report_writer,
                                            profile,
                                            expected_error,
                                            force_dtype=force_dtype,
                                            expected_df_dict=expected_df_dict)
