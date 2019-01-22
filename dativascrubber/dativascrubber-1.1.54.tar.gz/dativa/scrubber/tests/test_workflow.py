# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

import logging
import tempfile
import shutil
from datetime import datetime
import pandas as pd
from dativa.scrubber.tests import _BaseTest
from dativa.tools.pandas import CSVHandler
from dativa.scrubber import ScrubberValidationError, Scrubber, LoggingReportWriter, DefaultReportWriter


class WorkflowTests(_BaseTest):

    def test_report_writer(self):
        csv = CSVHandler(base_path=self.base_path)

        df = csv.get_dataframe("number/test_int_is_unique_dirty.csv", force_dtype=pd.np.float)

        writer = DefaultReportWriter()
        scrubber = Scrubber(report_writer=writer)

        report = scrubber.run(df=df,
                              config={"rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 1,
                                          "default_value": 0,
                                          "fallback_mode": "use_default",
                                          "fix_decimal_places": True,

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "maximum_value": 100.0,
                                          "minimum_value": 1.0,
                                          "skip_blank": True,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "TotalEpisodes"
                                  }]})

        self.assertEqual(str(report[0]).split(", ")[1],
                         "Field TotalEpisodes(Number): #26 modified/|Automatically fixed to 1 decimal places")
        self.assertEqual(str(report[1]).split(", ")[1],
                         "Field TotalEpisodes_clean(Number): #16 quarantined/|Removed duplicates")
        self.assertEqual(str(report[2]).split(", ")[1],
                         "Field TotalEpisodes(Number): #1 replaced/|Replaced with default value")

        self.assertEqual(report[0].get_log_dict()["field"], "TotalEpisodes")
        self.assertEqual(report[0].get_log_dict()["rule"], "Number")
        self.assertEqual(report[0].get_log_dict()["number_records"], 26)
        self.assertEqual(report[0].get_log_dict()["category"], "modified")
        self.assertEqual(report[0].get_log_dict()["description"], "Automatically fixed to 1 decimal places")

        self.assertEqual(report[0].get_records().shape, (26, 2))

    def test_log_report_writer(self):
        csv = CSVHandler(base_path=self.base_path)
        logger = logging.getLogger("dativa.scrubber.test")
        tempdir = tempfile.mkdtemp()

        df = csv.get_dataframe("number/test_int_is_unique_dirty.csv", force_dtype=pd.np.float)

        writer = LoggingReportWriter(logger=logger,
                                     quarantine_path=tempdir,
                                     error_severities=["quarantined"],
                                     warning_severities=["replaced"])
        scrubber = Scrubber(report_writer=writer)

        with self.assertLogs("dativa.scrubber.test") as logs:
            scrubber.run(df=df,
                         config={"rules": [
                             {
                                 "append_results": False,
                                 "params": {
                                     "attempt_closest_match": False,
                                     "decimal_places": 1,
                                     "default_value": 0,
                                     "fallback_mode": "use_default",
                                     "fix_decimal_places": True,

                                     "is_unique": True,
                                     "lookalike_match": False,
                                     "maximum_value": 100.0,
                                     "minimum_value": 1.0,
                                     "skip_blank": True,
                                     "string_distance_threshold": 0.7
                                 },
                                 "rule_type": "Number",
                                 "field": "TotalEpisodes"
                             }]})

            date = "{0:%Y%m%d%H%M%S}".format(datetime.now())
            self.assertEqual(logs.output,
                             [
                                 'INFO:dativa.scrubber.test:modified: #26 from TotalEpisodes : Automatically fixed to 1 decimal places [totalepisodes-number-{0}.csv]'.format(date),
                                 'ERROR:dativa.scrubber.test:quarantined: #16 from TotalEpisodes_clean : Removed duplicates [totalepisodes_clean-number-{0}.csv]'.format(date),
                                 'WARNING:dativa.scrubber.test:replaced: #1 from TotalEpisodes : Replaced with default value [totalepisodes-number-{0}.csv]'.format(date)]
                             )

        shutil.rmtree(tempdir)

    def test_lookalike(self):
        self._test_filter(dirty_file="generic/lookalike_dirty.csv",
                          clean_file="generic/lookalike_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": True,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": ".+",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "-1"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'favourite_singer',
                                  'rule': 'String',
                                  'number_records': 2,
                                  'category': 'replaced',
                                  'description': 'Lookalike match',
                                  'df': [[None, 'Bob Dylan'],
                                         [None, 'Taylor Swift']],

                              },
                          ])

    def test_lookalike_2(self):
        self._test_filter(dirty_file="generic/lookalike_dirty2.csv",
                          clean_file="generic/lookalike_clean2.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": True,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": ".+",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "2"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'favourite_singer',
                                  'rule': 'String',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Lookalike match',
                                  'df': [[None, 'Bob Dylan'],
                                         [None, 'Taylor Swift'],
                                         [None, 'David Bowie']],

                              },
                          ])

    def test_tsv(self):
        self._test_filter(dirty_file="generic/tsv_test.tsv",
                          clean_file="generic/tsv_clean2.tsv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": "^[0-9]*$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "1"
                                  }
                              ]
                          },
                          csv_delimiter="\t",
                          report=[
                              {

                                  'field': 'name',
                                  'rule': 'String',
                                  'number_records': 6,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [['the good'],
                                         ['the bad'],
                                         ['the ugly'],
                                         ['the worse'],
                                         ['the best'],
                                         ['the coolest']],

                              },
                          ])

    def test_tsv_2(self):
        self._test_filter(dirty_file="generic/tsv_test.tsv",
                          clean_file="generic/tsv_clean.tsv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": "^[0-9]*$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "0"
                                  }
                              ]
                          },
                          csv_delimiter="\t",
                          report=[
                              {

                                  'field': 'count',
                                  'rule': 'String',
                                  'number_records': 2,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [[-1],
                                         [-2]],

                              },
                          ])

    def test_workflow_invalid_rule_name(self):
        self._test_filter(dirty_file="generic/tsv_test.tsv",
                          clean_file="generic/tsv_clean.tsv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": "^[0-9]*$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Banana",
                                      "field": "0"
                                  }
                              ]
                          },
                          expected_error=ScrubberValidationError)

    def test_missing_field(self):
        self._test_filter(dirty_file="generic/tsv_test.tsv",
                          clean_file="generic/tsv_clean.tsv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "regex": "^[0-9]*$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "0"
                                  }
                              ]
                          },
                          expected_error=ScrubberValidationError)

    def test_bad_multicolumn(self):
        self._test_filter(dirty_file="generic/tsv_test.tsv",
                          clean_file="generic/tsv_clean.tsv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "regex": "^[0-9]*$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Session",
                                  }
                              ]
                          },
                          expected_error=ScrubberValidationError)

    def test_missing_rules(self):
        self._test_filter(dirty_file="generic/tsv_test.tsv",
                          clean_file="generic/tsv_clean.tsv",
                          config={"no_rules": 1},
                          expected_error=ScrubberValidationError)


class WorkflowTestsWithRounding(_BaseTest):
    """
    these tests combine lookalike and rounding tests
    """

    def test_no_report(self):
        with self.assertRaises(ValueError):
            self._test_filter(dirty_file="generic/lookalike_short.csv",
                              clean_file="generic/lookalike_short_clean.csv",
                              config={
                                  "rules": [
                                      {
                                          "params": {
                                              "fix_decimal_places": True,
                                              "fallback_mode": "remove_record",
                                              "minimum_value": 20,
                                              "decimal_places": 0,
                                              "maximum_value": 100
                                          },
                                          "field": "Age",
                                          "rule_type": "Number"
                                      },
                                      {
                                          "params": {
                                              "maximum_length": 10,
                                              "minimum_length": 0,
                                              "fallback_mode": "remove_record"
                                          },
                                          "field": "Gender",
                                          "rule_type": "String"
                                      },
                                      {
                                          "params": {
                                              "maximum_length": 20,
                                              "skip_blank": False,
                                              "fallback_mode": "use_default",
                                              "lookalike_match": True,
                                              "is_unique": False,
                                              "minimum_length": 1,
                                              "attempt_closest_match": False,
                                              "default_value": "xxxxxxxxxxxxxxx"
                                          },
                                          "field": "Favourite artist",
                                          "rule_type": "String"
                                      }]})

    def test_lookalike_short(self):
        self._test_filter(dirty_file="generic/lookalike_short.csv",
                          clean_file="generic/lookalike_short_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "params": {
                                          "fix_decimal_places": True,
                                          "fallback_mode": "remove_record",
                                          "minimum_value": 20,
                                          "decimal_places": 0,
                                          "maximum_value": 100
                                      },
                                      "field": "Age",
                                      "rule_type": "Number"
                                  },
                                  {
                                      "params": {
                                          "maximum_length": 10,
                                          "minimum_length": 0,
                                          "fallback_mode": "remove_record"
                                      },
                                      "field": "Gender",
                                      "rule_type": "String"
                                  },
                                  {
                                      "params": {
                                          "maximum_length": 20,
                                          "skip_blank": False,
                                          "fallback_mode": "use_default",
                                          "lookalike_match": True,
                                          "is_unique": False,
                                          "minimum_length": 1,
                                          "attempt_closest_match": False,
                                          "default_value": "xxxxxxxxxxxxxxx"
                                      },
                                      "field": "Favourite artist",
                                      "rule_type": "String"
                                  }]},
                          report=[
                              {

                                  'field': 'Age',
                                  'rule': 'Number',
                                  'number_records': 7,
                                  'category': 'modified',
                                  'description': 'Automatically fixed to 0 decimal places',
                                  'df': [[50, 'M', 'Bob Dylan', 50],
                                         [50, 'M', 'Bob Dylan', 50],
                                         [20, 'F', 'Taylor Swift', 20],
                                         [22, 'F', 'Rihanna', 22],
                                         [23, 'F', 'Rihanna', 23],
                                         [50, 'M', None, 50],
                                         [23, 'F', None, 23]],

                              },
                              {

                                  'field': 'Favourite artist',
                                  'rule': 'String',
                                  'number_records': 2,
                                  'category': 'replaced',
                                  'description': 'Lookalike match',
                                  'df': [[None, 'Bob Dylan'],
                                         [None, 'Rihanna']],

                              },
                          ]
                          )
