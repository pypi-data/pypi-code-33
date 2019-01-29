# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

import pandas as pd
from dativa.scrubber.tests import _BaseTest
from dativa.tools.pandas import CSVHandler
from dativa.scrubber import Scrubber, ScrubberValidationError

class DateTests(_BaseTest):

    def test_date(self):
        self._test_filter(dirty_file="date/date_format.csv",
                          clean_file="date/date_format_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%d-%m-%Y %H:%M:%S",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",
                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "range_check": "rolling",
                                          "range_maximum": "10000",
                                          "range_minimum": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "Date"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ])

    def test_date_1(self):
        self._test_filter(dirty_file="date/date_format.csv",
                          clean_file="date/date_format_clean1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%d-%m-%Y %H:%M:%S",
                                          "default_value": "",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "01-01-2028 00:00:00",
                                          "range_minimum": "01-01-2017 10:03:16",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "Date"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [['30-03-2010 10:03:26'],
                                         ['31-02-2027 10:99:16'],
                                         ['05-04-2027 25:03:16']],

                              },
                          ])

    def test_date_2(self):
        self._test_filter(dirty_file="date/date_format.csv",
                          clean_file="date/date_format_clean2.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%d-%m-%Y %H:%M:%S",
                                          "default_value": "",
                                          "fallback_mode": "do_not_replace",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "range_check": "none",
                                          "range_maximum": "",
                                          "range_minimum": "",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "Date"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 2,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [['31-02-2027 10:99:16', '31-02-2027 10:99:16'],
                                         ['05-04-2027 25:03:16', '05-04-2027 25:03:16']],

                              },
                          ])

    def test_date_3(self):
        self._test_filter(dirty_file="date/date_format1.csv",
                          clean_file="date/date_format1_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%d-%m-%Y",
                                          "default_value": "N/A",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "02-05-2021",
                                          "range_minimum": "01-01-2001",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "Date"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 10,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [['19-19-2001'],
                                         ['05-04-2103'],
                                         ['06-04-2103'],
                                         ['07-04-2103'],
                                         ['08-04-2103'],
                                         ['09-04-2103'],
                                         [None],
                                         ['748949+84'],
                                         ['231514'],
                                         ['45457']],

                              },
                          ]
                          )

    def test_date_4(self):
        self._test_filter(dirty_file="date/date_is_unique_dirty.csv",
                          clean_file="date/date_is_unique_cleaned.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%d/%m/%Y %H:%M:%S",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "24/12/2017 07:01:15",
                                          "range_minimum": "18/12/2017 07:01:15",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "Date"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 2,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['18/12/2017 07:01:15'],
                                         ['19/12/2017 07:01:15']],

                              },
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 1,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['25/12/2017 07:01:15', 'N/A']],

                              },
                          ])

    def test_date_5(self):
        self._test_filter(dirty_file="date/date_format_2.csv",
                          clean_file="date/date_format_2.csv",
                          config={'rules': [
                              {'field': 'PREV_CHECKIN_DATE',
                               'rule_type': 'Date',
                               'params': {'date_format': '%Y-%m-%d %H:%M:%S.%f', 'range_check': 'none',
                                          'fallback_mode': 'remove_record'}},
                              {'field': 'CHECKIN_DATE',
                               'rule_type': 'Date',
                               'params': {'date_format': '%Y-%m-%d %H:%M:%S.%f', 'range_check': 'none',
                                          'fallback_mode': 'remove_record'}}, ]},
                          csv_delimiter="|",
                          report=[])

    def test_date_6(self):
        self._test_filter(dirty_file="date/date_format_2.csv",
                          clean_file="date/date_format_2_clean.csv",
                          config={'rules': [
                              {'field': 'PREV_CHECKIN_DATE',
                               'rule_type': 'Date',
                               'params': {'date_format': '%Y/%m/%d %H:%M:%S.%f', 'range_check': 'none',
                                          'fallback_mode': 'remove_record'}},
                              {'field': 'CHECKIN_DATE',
                               'rule_type': 'Date',
                               'params': {'date_format': '%Y/%m/%d %H:%M:%S.%f', 'range_check': 'none',
                                          'fallback_mode': 'remove_record'}}, ]},
                          csv_delimiter="|",
                          report=[
                              {

                                  'field': 'PREV_CHECKIN_DATE',
                                  'rule': 'Date',
                                  'number_records': 11,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [['2018-02-28 00:00:00.000000'],
                                         ['2018-02-28 00:00:00.000000'],
                                         ['2018-02-25 00:00:00.000000'],
                                         ['2018-02-28 00:00:00.000000'],
                                         ['2018-02-27 00:00:00.000000'],
                                         ['2018-02-24 00:00:00.000000'],
                                         ['2018-02-28 00:00:00.000000'],
                                         ['2018-02-28 00:00:00.000000'],
                                         ['2018-02-28 00:00:00.000000'],
                                         ['2018-02-28 00:00:00.000000'],
                                         ['2018-02-28 00:00:00.000000']],

                              },
                          ])

    def test_date_epoch(self):
        self._test_filter(dirty_file="date/check_epoch_time.csv",
                          clean_file="date/check_epoch_time_cleaned1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%s",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "1511373354",
                                          "range_minimum": "1511344324",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "utc_air_start_epoch"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'utc_air_start_epoch',
                                  'rule': 'Date',
                                  'number_records': 14,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [[1511379769, 'N/A'],
                                         [1511343124, 'N/A'],
                                         [1511336569, 'N/A'],
                                         [1511329924, 'N/A'],
                                         [1511328724, 'N/A'],
                                         [1511322169, 'N/A'],
                                         [1511315524, 'N/A'],
                                         [1511314324, 'N/A'],
                                         [1511394199, 'N/A'],
                                         [1511393209, 'N/A'],
                                         [1511386999, 'N/A'],
                                         [1511386009, 'N/A'],
                                         [1511379799, 'N/A'],
                                         [1511378809, 'N/A']],

                              },
                          ])

    def test_date_epoch_2(self):
        self._test_filter(dirty_file="date/check_epoch_time.csv",
                          clean_file="date/check_epoch_time_cleaned1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%s",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "1511373354",
                                          "range_minimum": "banana",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "utc_air_start_epoch"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ],
                          expected_error=ScrubberValidationError)

    def test_date_range_error(self):
        self._test_filter(dirty_file="date/check_epoch_time.csv",
                          clean_file="date/check_epoch_time_cleaned1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%s",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_minimum": "1511344324",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "utc_air_start_epoch"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ],
                          expected_error=ScrubberValidationError)

    def test_date_range_error_2(self):
        self._test_filter(dirty_file="date/check_epoch_time.csv",
                          clean_file="date/check_epoch_time_cleaned1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%s",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "1511373354",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "utc_air_start_epoch"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ],
                          expected_error=ScrubberValidationError)

    def test_date_range_error_3(self):
        self._test_filter(dirty_file="date/check_epoch_time.csv",
                          clean_file="date/check_epoch_time_cleaned1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%s",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "1st January 2001",
                                          "range_minimum": "1511344324",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "utc_air_start_epoch"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ],
                          expected_error=ScrubberValidationError)

    def test_date_range_error_4(self):
        self._test_filter(dirty_file="date/check_epoch_time.csv",
                          clean_file="date/check_epoch_time_cleaned1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%s",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "1511373354",
                                          "range_minimum": "1st January 2001",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "utc_air_start_epoch"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ],
                          expected_error=ScrubberValidationError)

    def test_date_range_error_5(self):
        self._test_filter(dirty_file="date/check_epoch_time.csv",
                          clean_file="date/check_epoch_time_cleaned1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%s",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "range_check": "fixed",
                                          "range_maximum": "1511373354",
                                          "range_minimum": "2511344324",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "utc_air_start_epoch"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ],
                          expected_error=ScrubberValidationError)

    def test_date_error_6(self):
        self._test_filter(dirty_file="date/date_format.csv",
                          clean_file="date/date_format_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%d-%m-%Y %H:%M:%S",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",
                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "range_check": "rolling",
                                          "range_maximum": "10000",
                                          "range_minimum": "1st January 2000",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "Date"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ],
                          expected_error=ScrubberValidationError)

    def test_date_error_7(self):
        self._test_filter(dirty_file="date/date_format.csv",
                          clean_file="date/date_format_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "date_format": "%d-%m-%Y %H:%M:%S",
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",
                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "range_check": "rolling",
                                          "range_maximum": "1st January 2000",
                                          "range_minimum": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Date",
                                      "field": "Date"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Date',
                                  'rule': 'Date',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['30-03-2010 10:03:26', 'N/A'],
                                         ['31-02-2027 10:99:16', 'N/A'],
                                         ['05-04-2027 25:03:16', 'N/A']],

                              },
                          ],
                          expected_error=ScrubberValidationError)

    def test_date_as_timestamp(self):
        csv = CSVHandler(base_path=self.base_path)

        df = csv.get_dataframe("anonymization/emails.csv")

        df.date = pd.to_datetime(df.date)

        scrubber = Scrubber()

        scrubber.run(df=df,
                     config={"rules": [
                         {
                             "rule_type": "String",
                             "field": "to",
                             "params": {
                                 "minimum_length": 5,
                                 "maximum_length": 1024,
                                 "regex": "[^@]+@[^\\.]..*[^\\.]",
                                 "fallback_mode": "remove_record",
                                 "encrypt": True,
                                 "public_key": """-----BEGIN PUBLIC KEY-----
                           MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDmPPm5UC8rXn4uX37m4tN/j4T
                           MAhUVyxN7V7QxMF3HDg5rkl/Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10
                           sZI0kIrkizlKaB/20Q4P1kYOCgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0
                           DoNemKEpyCt2dZTaQwIDAQAB
                           -----END PUBLIC KEY-----"""
                             }},
                         {
                             "rule_type": "Date",
                             "field": "date",
                             "params": {
                                 "date_format": "%Y-%m-%d %H:%M:%S",
                                 "fallback_mode": "remove_record"
                             }
                         }]})

        scrubber.run(df=df,
                     config={"rules": [
                         {
                             "rule_type": "String",
                             "field": "to",
                             "params": {
                                 "minimum_length": 5,
                                 "maximum_length": 1024,
                                 "regex": "[^@]+@[^\\.]..*[^\\.]",
                                 "fallback_mode": "remove_record",
                                 "decrypt": True,
                                 "private_key": """-----BEGIN RSA PRIVATE KEY-----
                            MIICXQIBAAKBgQDDmPPm5UC8rXn4uX37m4tN/j4TMAhUVyxN7V7QxMF3HDg5rkl/
                            Ju53DPJbv59TCvlTCXw1ihp9asVyyYpCqrsKCh10sZI0kIrkizlKaB/20Q4P1kYO
                            Cgv4Cwds7Iu2y0TFwDosK9a7MPR9IksL7QRWKjD0DoNemKEpyCt2dZTaQwIDAQAB
                            AoGBAIxvLv8irp5JN3+7Ppb+EMDIwCzqmbBkfmzc9uyRuA4a9suDNUXT3/ceFoyF
                            QpFPGb/i2YlfRLGzjVxjE5/WET9bf//ATOkZyn2sl4jBGs9WIF4by+246E+dfol9
                            /326rSpJjVeklmELU3nJp4ViZzYX+Cwc0rucpZLMqLUUFbvhAkEAzP+WSV2cp5w4
                            E1OBDM7cyq3lneWP0N1OdteZPZlJT0ojsQuoggqvcUMeC/eSoaHyZGN7GS4OVtaC
                            BR++kkPiCwJBAPRCnk4FmeLtnDpTX7KV8a766jSqkDzqEKVVqoGfLYCe0uaWFcwK
                            MKBik0GJ6tFLg9JvJMbP1+eD8+2uQD7rg6kCQDNghyDiBkX3oBIv5nL4UVu2k4qs
                            IwwcuvKL/Er05OurUCCqJFRbKzc+tAQZyzUZKm/AgvR/l3ZqEnIIT7HGs5sCQDej
                            NQvwmqzmEr/2XcYAAZ0p6k80ysYVStVePghoiaTSiJedeDmR2KGv0nsLP0GNQemd
                            B3OBxFwn4lgxaNDsNIECQQCTrHWrS/v5rh5sNNPC8dn7e4TThuvQ5l/mv5zTZHu9
                            rtdkt0kn4xawfR5p0nrW6HL2M3pRbJ0obi6h//HZc8KX
                            -----END RSA PRIVATE KEY-----"""
                             }}]})

        self._compare_df_to_file(csv, df, "anonymization/emails.csv")
