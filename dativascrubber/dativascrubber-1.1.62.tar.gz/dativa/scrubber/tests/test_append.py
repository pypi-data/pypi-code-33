# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from dativa.scrubber.tests import _BaseTest


class AppendTests(_BaseTest):

    def test_append(self):
        self._test_filter(dirty_file="generic/test_cities_dirty1.csv",
                          clean_file="generic/test_cities_dirty_clean1.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "String",
                                      "field": "-2",
                                      "append_results": True,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "N/A",
                                          "fallback_mode": "use_default",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": "^[0-9]*$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                  },
                                  {
                                      "rule_type": "Lookup",
                                      "field": "-1",
                                      "append_results": True,
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
                                  }
                              ]
                          },
                          report=[{'field': 'city',
                                   'rule': 'Lookup',
                                   'number_records': 4,
                                   'category': 'replaced',
                                   'description': 'Best match',
                                   'df': [['Bsitrol', 'Bristol'],
                                          ['London', 'Croydon'],
                                          ['Lverpool', 'Liverpool'],
                                          ['méémlent', 'élément']]},
                                  {'field': 'city',
                                   'rule': 'Lookup',
                                   'number_records': 3,
                                   'category': 'ignored',
                                   'description': 'No changes made',
                                   'df': [['Bath', 'Bath'],
                                          ['Btha', 'Btha'],
                                          ['Lndon', 'Lndon']]}])

    def test_append_1(self):
        self._test_filter(dirty_file="generic/ip_list.csv",
                          clean_file="generic/ip_list1.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "String",
                                      "field": "0",
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "",
                                          "fallback_mode": "do_not_replace",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                  },
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "number",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'ip_addr',
                                  'rule': 'String',
                                  'number_records': 1,
                                  'category': 'replaced',
                                  'description': 'Best match',
                                  'df': [['192.16.8.0.2', '192.168.0.2']],

                              },
                              {

                                  'field': 'number',
                                  'rule': 'Uniqueness',
                                  'number_records': 18,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110],
                                         ['192.168.0.3', 110]],

                              },
                          ])

    def test_append_2(self):
        self._test_filter(dirty_file="generic/ip_list.csv",
                          clean_file="generic/ip_list1_new.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "String",
                                      "field": "0",
                                      "append_results": True,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "",
                                          "fallback_mode": "do_not_replace",

                                          "is_unique": False,
                                          "lookalike_match": False,
                                          "maximum_length": 1000,
                                          "minimum_length": 0,
                                          "regex": "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                  },
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "number",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'ip_addr',
                                  'rule': 'String',
                                  'number_records': 1,
                                  'category': 'replaced',
                                  'description': 'Best match',
                                  'df': [['192.16.8.0.2', '192.168.0.2']],

                              },
                              {

                                  'field': 'number',
                                  'rule': 'Uniqueness',
                                  'number_records': 18,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3'],
                                         ['192.168.0.3', 110, '192.168.0.3']],

                              },
                          ])
