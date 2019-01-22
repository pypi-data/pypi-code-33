# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from dativa.scrubber.tests import _BaseTest
from dativa.scrubber import ScrubberValidationError


class StringTests(_BaseTest):

    def test_string(self):
        self._test_filter(dirty_file="string/test_string_is_unique_dirty.csv",
                          clean_file="string/test_string_is_unique_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "N/A",
                                          "fallback_mode": "remove_record",

                                          "is_unique": True,
                                          "lookalike_match": False,
                                          "maximum_length": 15,
                                          "minimum_length": 0,
                                          "regex": "",
                                          "skip_blank": False
                                      },
                                      "rule_type": "String",
                                      "field": "Name"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Name',
                                  'rule': 'String',
                                  'number_records': 5,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['Sarvesh'],
                                         ['Sarvesh'],
                                         ['Narendra'],
                                         ['Harshad'],
                                         ['sivaji']],

                              },
                          ]
                          )

    def test_string_2(self):
        self._test_filter(dirty_file="string/test_string_dirty.csv",
                          clean_file="string/test_string_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 15,
                                          "minimum_length": 0,
                                          "regex": "^[A-z\\s]{1,}$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "Name"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Name',
                                  'rule': 'String',
                                  'number_records': 10,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['Loida Lajeunesse', 'N/A'],
                                         ['Michael Markwell', 'N/A'],
                                         ['Iris Illingworth', 'N/A'],
                                         ['Samatha Severance', 'N/A'],
                                         ['Anneliese Angers', 'N/A'],
                                         ['Polly Porterfield', 'N/A'],
                                         ['Bernadette Bratt', 'N/A'],
                                         ['Margarito Molloy', 'N/A'],
                                         ['FerNonede Fuentes', 'N/A'],
                                         ['Kurtis K3en', 'N/A']],

                              },
                          ])

    def test_string_3(self):
        self._test_filter(dirty_file="string/test_string_dirty1.csv",
                          clean_file="string/test_string_clean1.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 15,
                                          "minimum_length": 0,
                                          "regex": ".+",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "Name"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Name',
                                  'rule': 'String',
                                  'number_records': 12,
                                  'category': 'replaced',
                                  'description': 'Replaced with default value',
                                  'df': [['Loida Lajeunesse', 'N/A'],
                                         [None, 'N/A'],
                                         ['Michael Markwell', 'N/A'],
                                         ['Iris Illingworth', 'N/A'],
                                         ['Samatha Severance', 'N/A'],
                                         ['Anneliese Angers', 'N/A'],
                                         ['Polly Porterfield', 'N/A'],
                                         ['Bernadette Bratt', 'N/A'],
                                         [None, 'N/A'],
                                         ['Margarito Molloy', 'N/A'],
                                         ['FerNonede Fuentes', 'N/A'],
                                         [None, 'N/A']],

                              },
                          ])

    def test_string_4(self):
        self._test_filter(dirty_file="string/test_string_dirty.csv",
                          clean_file="string/test_string_clean2.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "N/A",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 15,
                                          "minimum_length": 0,
                                          "regex": "",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "Name"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Name',
                                  'rule': 'String',
                                  'number_records': 9,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [['Loida Lajeunesse'],
                                         ['Michael Markwell'],
                                         ['Iris Illingworth'],
                                         ['Samatha Severance'],
                                         ['Anneliese Angers'],
                                         ['Polly Porterfield'],
                                         ['Bernadette Bratt'],
                                         ['Margarito Molloy'],
                                         ['FerNonede Fuentes']],

                              },
                          ])

    def test_string_ints(self):
        self._test_filter(dirty_file="string/test_string_dirty_ints.csv",
                          clean_file="string/test_string_clean_ints.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "fallback_mode": "remove_record",
                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 10,  # but we're filtering with regex
                                          "minimum_length": 0,
                                          "regex": "^\d$",  # number, length 1
                                          "skip_blank": False,
                                      },
                                      "rule_type": "String",
                                      "field": "integer"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'integer',
                                  'rule': 'String',
                                  'number_records': 1,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [[10]],

                              },
                          ])

    def test_string_FpValidationError(self):
        self._test_filter(dirty_file="string/test_string_dirty.csv",
                          clean_file="string/test_string_clean2.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "N/A",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 15,
                                          "minimum_length": 0,
                                          "regex": "**",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "Name"
                                  }
                              ]
                          },
                          expected_error=ScrubberValidationError)

    def test_string_FpValidationError2(self):
        self._test_filter(dirty_file="string/test_string_dirty.csv",
                          clean_file="string/test_string_clean2.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "N/A",
                                          "fallback_mode": "remove_record",
                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 15,
                                          "minimum_length": 0,
                                          "regex": "*",
                                          "not_a_field": True,
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "Name"
                                  }
                              ]
                          },
                          expected_error=ScrubberValidationError)

    def test_string_5(self):
        self._test_filter(dirty_file="string/test_string_dirty.csv",
                          clean_file="string/test_string_clean_removed_all.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "N/A",
                                          "fallback_mode": "remove_record",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 15,
                                          "minimum_length": 0,
                                          "regex": ".*",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "NameNotThere"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'NameNotThere',
                                  'rule': 'String',
                                  'number_records': 50,
                                  'category': 'quarantined',
                                  'description': 'File did not contain required column',
                                  'df': [['Glinda Geisler', None],
                                         ['Loida Lajeunesse', None],
                                         ['Dani Deboer', None],
                                         ['Trena Teti', None],
                                         ['Vanda Viers', None],
                                         ['Eveline Eddy', None],
                                         ['Zora Zajac', None],
                                         ['Nicole Nickens', None],
                                         ['Suzy Stetler', None],
                                         ['Karine Kissee', None],
                                         ['Deidre Durrell', None],
                                         ['Nery Novy', None],
                                         ['Michael Markwell', None],
                                         ['FerNoneda Faison', None],
                                         ['Tyler Thrall', None],
                                         ['Tianna Tenner', None],
                                         ['Iris Illingworth', None],
                                         ['Samatha Severance', None],
                                         ['Anneliese Angers', None],
                                         ['Polly Porterfield', None],
                                         ['Bernadette Bratt', None],
                                         ['Siu Siddiqi', None],
                                         ['Susan Salmon', None],
                                         ['Dexter Desch', None],
                                         ['Amber Avis', None],
                                         ['Jackson Jetton', None],
                                         ['Vernia Vue', None],
                                         ['Sanda Sandoval', None],
                                         ['Margarito Molloy', None],
                                         ['Timothy Tranmer', None],
                                         ['Gertie Godin', None],
                                         ['Jenae Jack', None],
                                         ['FerNonede Fuentes', None],
                                         ['Yaeko Yoshimura', None],
                                         ['Lovetta Lowrey', None],
                                         ['Eartha Ellisor', None],
                                         ['Elane Edds', None],
                                         ['Emilie Ecker', None],
                                         ['Annette Alcaraz', None],
                                         ['Larue Liptak', None],
                                         ['Talia Tugwell', None],
                                         ['Sachiko Suniga', None],
                                         ['Les Lieser', None],
                                         ['Emeline Ekberg', None],
                                         ['Whitney Wymore', None],
                                         ['Kurtis K3en', None],
                                         ['Lloyd Landa', None],
                                         ['Gregorio Gorder', None],
                                         ['Chas Carneva', None],
                                         ['Lashaunda Lindl', None]],

                              },
                          ])

    def test_string_FpValidationError_2(self):
        self._test_filter(dirty_file="string/test_string_dirty.csv",
                          clean_file="string/test_string_clean2.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": False,
                                          "default_value": "N/A",
                                          "fallback_mode": "remove_record",
                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 15,
                                          "minimum_length": 20,
                                          "regex": ".*",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "Name"
                                  }
                              ]
                          },
                          expected_error=ScrubberValidationError)
