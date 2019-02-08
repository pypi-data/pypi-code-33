# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

import pandas as pd
from dativa.tools.pandas import CSVHandler
from dativa.scrubber.tests import _BaseTest
from dativa.scrubber import Scrubber


class SkipBlankTests(_BaseTest):

    def test_skip_blank(self):
        self._test_filter(dirty_file="generic/names_blank.csv",
                          clean_file="generic/names_blank_skip.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": ".+",
                                          "skip_blank": True,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "0"
                                  }
                              ]
                          },
                          report=[])

    def test_skip_blank_1(self):
        self._test_filter(dirty_file="generic/names_blank.csv",
                          clean_file="generic/names_blank_na.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": ".+",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "0"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Name',
                                  'rule': 'String',
                                  'number_records': 1,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [[None, 'N/A']],

                              },
                          ])

    def test_skip_blank_2(self):
        self._test_filter(dirty_file="generic/test_cities_dirty_skip_blank.csv",
                          clean_file="generic/test_cities_dirty_skip_blank_na.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "Banana",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/test_cities_reference.csv",

                                          "reference_field": "-1",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "1"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'city',
                                  'rule': 'Lookup',
                                  'number_records': 23,
                                  'category': 'replaced',
                                  'description': 'Best match',
                                  'df': [['Bsitrol', 'Bristol'],
                                         ['Lverpool', 'Liverpool'],
                                         ['méémlent', 'élément'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon']],

                              },
                              {

                                  'field': 'city',
                                  'rule': 'Lookup',
                                  'number_records': 8,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [['Bath', 'Bath'],
                                         ['Btha', 'Btha'],
                                         ['Lndon', 'Lndon'],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None]],

                              },
                          ])

    def test_skip_blank_3(self):
        self._test_filter(dirty_file="generic/email_test.csv",
                          clean_file="generic/email_test_skip_blank.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",
                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": ".+",
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "0"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'e-mail',
                                  'rule': 'String',
                                  'number_records': 1,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [[None, 'N/A']],

                              },
                          ])

    def test_skip_blank_native(self):
        csv = CSVHandler(base_path=self.base_path)

        df = csv.get_dataframe("number/test_int_is_unique_dirty.csv", force_dtype=pd.np.float)

        fp = Scrubber()

        fp.run(df=df,
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

        self._compare_df_to_file(csv, df, "number/test_int_is_unique_clean.csv")

    def test_skip_blank_columns(self):
        self._test_filter(dirty_file="generic/email_test.csv",
                          clean_file="generic/email_missing_field.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                      },
                                      "rule_type": "String",
                                      "field": "not_a_field"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'not_a_field',
                                  'rule': 'String',
                                  'number_records': 7,
                                  'category': 'quarantined',
                                  'description': 'File did not contain required column',
                                  'df': [['n@gmail.com', 0, None],
                                         ['p@gmail.com', 1, None],
                                         ['h@gmail.com', 0, None],
                                         ['s@gmail.com', 0, None],
                                         ['l@gmail.com', 1, None],
                                         ['v@gmail.com', 0, None],
                                         [None, 0, None]],

                              },
                          ])
