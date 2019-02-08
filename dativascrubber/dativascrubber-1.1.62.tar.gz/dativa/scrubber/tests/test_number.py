# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from dativa.scrubber.tests import _BaseTest
from dativa.scrubber import ScrubberValidationError


class NumberTests(_BaseTest):

    def test_number(self):
        self._test_filter(dirty_file="number/test_int_range_dirty.csv",
                          clean_file="number/test_int_range_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 2,
                                          "default_value": 0,
                                          "fallback_mode": "use_default",
                                          "fix_decimal_places": False,

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_value": 1.0,
                                          "minimum_value": 0.0,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Number',
                                  'rule': 'Number',
                                  'number_records': 4,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['1.02', 0],
                                         ['0', 0],
                                         ['-1', 0],
                                         ['fjidos', 0]],

                              },
                          ])

    def test_number_1(self):
        self._test_filter(dirty_file="number/test_int_range_dirty1.csv",
                          clean_file="number/test_int_range_clean1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 2,
                                          "default_value": 0,
                                          "fallback_mode": "use_default",
                                          "fix_decimal_places": False,

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_value": 1.0,
                                          "minimum_value": -1.0,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Number',
                                  'rule': 'Number',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['1.02', 0],
                                         ['0', 0],
                                         ['fjidos', 0]],

                              },
                          ])

    def test_number_2(self):
        self._test_filter(dirty_file="number/test_int_range_dirty2.csv",
                          clean_file="number/test_int_range_clean2.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 2,
                                          "default_value": 0,
                                          "fallback_mode": "use_default",
                                          "fix_decimal_places": False,

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_value": -1.0,
                                          "minimum_value": -5.0,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Number',
                                  'rule': 'Number',
                                  'number_records': 11,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['-0.00', 0],
                                         ['-0.51', 0],
                                         ['-0.43', 0],
                                         ['0.00', 0],
                                         ['0.01', 0],
                                         ['0.02', 0],
                                         ['1.00', 0],
                                         ['1.02', 0],
                                         ['0', 0],
                                         ['fjidos', 0],
                                         ['jhjk', 0]],

                              },
                          ])

    def test_number_3(self):
        self._test_filter(dirty_file="number/test_int_range_dirty2.csv",
                          clean_file="number/test_int_range_clean2dp.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 2,
                                          "default_value": 0,
                                          "fallback_mode": "use_default",
                                          "fix_decimal_places": False,

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_value": 10.0,
                                          "minimum_value": -10.0,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Number',
                                  'rule': 'Number',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['0', 0],
                                         ['fjidos', 0],
                                         ['jhjk', 0]],

                              },
                          ]
                          )

    def test_number_4(self):
        self._test_filter(dirty_file="number/test_int_is_unique_dirty.csv",
                          clean_file="number/test_int_is_unique_clean.csv",
                          config={
                              "rules": [
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
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "TotalEpisodes"
                                  }
                              ]
                          },
                          report=[
                              {
                                  'field': 'TotalEpisodes',
                                  'rule': 'Number',
                                  'number_records': 26,
                                  'category': 'modified',
                                  'description': 'Automatically fixed to 1 decimal places',
                                  'df': [[1.3, 1.3],
                                         [19., 19.],
                                         [19., 19.],
                                         [19.001, 19.],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [1.4, 1.4],
                                         [2.1, 2.1],
                                         [2.1, 2.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [5., 5.],
                                         [5., 5.],
                                         [5.1, 5.1],
                                         [51.1, 51.1],
                                         [5.1, 5.1],
                                         [1.9, 1.9],
                                         [1.9, 1.9],
                                         [1.9, 1.9],
                                         [1., 1.],
                                         [1., 1.]]
                              },
                              {
                                  'field': 'TotalEpisodes_clean',
                                  'rule': 'Number',
                                  'number_records': 16,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [[19., 19.],
                                         [19.001, 19.],
                                         [19.1, 19.1],
                                         [2.1, 2.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [19.1, 19.1],
                                         [5., 5.],
                                         [5.1, 5.1],
                                         [1.9, 1.9],
                                         [1.9, 1.9],
                                         [1., 1.]]
                              },
                              {
                                  'field': 'TotalEpisodes',
                                  'rule': 'Number',
                                  'number_records': 1,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [[199.1, 0.]]
                              }]
                          )

    def test_number_5(self):
        self._test_filter(dirty_file="number/test_int_is_unique_dirty.csv",
                          clean_file="number/test_int_is_unique_clean2.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 1,
                                          "default_value": 0,
                                          "fallback_mode": "use_default",
                                          "fix_decimal_places": True,

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_value": 100.0,
                                          "minimum_value": 1.0,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "TotalEpisodes"
                                  }
                              ]
                          },
                          report=[{
                                 'field': 'TotalEpisodes',
                                 'rule': 'Number',
                                 'number_records': 26,
                                 'category': 'modified',
                                 'description': 'Automatically fixed to 1 decimal places',
                                 'df': [[1.3, 1.3],
                                        [19., 19.],
                                        [19., 19.],
                                        [19., 19.],
                                        [19.1, 19.1],
                                        [19.1, 19.1],
                                        [1.4, 1.4],
                                        [2.1, 2.1],
                                        [2.1, 2.1],
                                        [19.1, 19.1],
                                        [19.1, 19.1],
                                        [19.1, 19.1],
                                        [19.1, 19.1],
                                        [19.1, 19.1],
                                        [19.1, 19.1],
                                        [19.1, 19.1],
                                        [5., 5.],
                                        [5., 5.],
                                        [5.1, 5.1],
                                        [51.1, 51.1],
                                        [5.1, 5.1],
                                        [1.9, 1.9],
                                        [1.9, 1.9],
                                        [1.9, 1.9],
                                        [1., 1.],
                                        [1., 1.]]
                                 },
                                 {
                                      'field': 'TotalEpisodes',
                                      'rule': 'Number',
                                      'number_records': 1,
                                      'category': 'replaced',
                                      'description': 'Replaced with default value',
                                      'df': [[199.1, 0.]]
                                 }]
                          )

    def test_number_6(self):
        self._test_filter(dirty_file="number/test_int_range_dirty3.csv",
                          clean_file="number/test_int_range_clean3.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "decimal_places": 2,
                                          "fallback_mode": "remove_record",
                                          "fix_decimal_places": True,
                                          "maximum_value": 5.0,
                                          "minimum_value": -5.0,
                                          "skip_blank": True
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Number',
                                  'rule': 'Number',
                                  'number_records': 13,
                                  'category': 'modified',
                                  'description': 'Automatically fixed to 2 decimal places',
                                  'df': [[0.0, '0.00'],
                                         [-0.51, '-0.51'],
                                         [-0.43, '-0.43'],
                                         [0.0, '0.00'],
                                         [0.01, '0.01'],
                                         [0.02, '0.02'],
                                         [1.0, '1.00'],
                                         [1.02, '1.02'],
                                         [0.0, '0.00'],
                                         [-1.0, '-1.00'],
                                         [-3.12, '-3.12'],
                                         [-1.32, '-1.32'],
                                         [-4.0, '-4.00']],

                              },
                          ])

    def test_number_7(self):
        self._test_filter(dirty_file="number/test_int_range_dirty_4.csv",
                          clean_file="number/test_int_range_clean_3.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "decimal_places": 2,
                                          "fallback_mode": "remove_record",
                                          "fix_decimal_places": False,
                                          "maximum_value": 5.0,
                                          "minimum_value": -5.0,
                                          "skip_blank": True
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Number',
                                  'rule': 'Number',
                                  'number_records': 1,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [[0.001]],

                              },
                          ])

    def test_number_0dp(self):
        self._test_filter(dirty_file="number/test_int_range_dirty.csv",
                          clean_file="number/test_int_range_clean_0dp.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 0,
                                          "default_value": 0,
                                          "fallback_mode": "use_default",
                                          "fix_decimal_places": True,

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_value": 1,
                                          "minimum_value": 0,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Number',
                                  'rule': 'Number',
                                  'number_records': 4,
                                  'category': 'modified',
                                  'description': 'Automatically fixed to 0 decimal places',
                                  'df': [['0.00', '0'],
                                         ['0.01', '0'],
                                         ['0.02', '0'],
                                         ['1.00', '1']],

                              },
                              {

                                  'field': 'Number',
                                  'rule': 'Number',
                                  'number_records': 3,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['1.02', 0],
                                         ['-1', 0],
                                         ['fjidos', 0]],

                              },
                          ])

    def test_number_invalid(self):
        self._test_filter(dirty_file="number/test_int_range_dirty.csv",
                          clean_file="number/test_int_range_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 0,
                                          "default_value": 0,
                                          "fallback_mode": "invalid",
                                          "fix_decimal_places": False,

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_value": 1,
                                          "minimum_value": 0,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          expected_error=ScrubberValidationError)

    def test_number_invalid_max_less_than_min(self):
        self._test_filter(dirty_file="number/test_int_range_dirty.csv",
                          clean_file="number/test_int_range_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "decimal_places": 0,
                                          "default_value": 0,
                                          "fallback_mode": "use_default",
                                          "fix_decimal_places": False,

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_value": 1,
                                          "minimum_value": 2,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Number",
                                      "field": "Number"
                                  }
                              ]
                          },
                          expected_error=ScrubberValidationError)
