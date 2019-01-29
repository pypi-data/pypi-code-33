# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from dativa.scrubber.tests import _BaseTest
from dativa.scrubber import ScrubberTooManyRecordsError, DefaultProfile
from dativa.tools.pandas import FpCSVEncodingError


class ProfileTests(_BaseTest):
    """Testing for user_subscriptions tests"""

    def test_profile(self):
        profile = DefaultProfile()

        self._test_filter(
            dirty_file="generic/Genres_Master.csv",
            clean_file="generic/Genres_Master.csv",
            config={"rules": [{"field": 0,
                               "rule_type": "String",
                               "params": {
                                   "regex": ".+",
                                   "fallback_mode": "use_default",
                                   "skip_blank": False,
                                   "minimum_length": 0,
                                   "maximum_length": 1024,
                                   "default_value": "N/A",
                                   "attempt_closest_match": False
                               }}]},
            profile=profile,
            report=[]
        )

        profile.maximum_records = 100

        self._test_filter(
            dirty_file="generic/Genres_Master.csv",
            clean_file="generic/Genres_Master.csv",
            config={"rules": [{"field": 0,
                               "rule_type": "String",
                               "params": {
                                   "regex": ".+",
                                   "fallback_mode": "use_default",
                                   "skip_blank": False,
                                   "minimum_length": 0,
                                   "maximum_length": 1024,
                                   "default_value": "N/A",
                                   "attempt_closest_match": False
                               }}]},
            profile=profile,
            expected_error=ScrubberTooManyRecordsError
        )

    def test_lookalike(self):
        profile = DefaultProfile()
        profile.maximum_records_lookalike = 1

        self._test_filter(dirty_file="generic/lookalike_dirty.csv",
                          clean_file="generic/lookalike_dirty.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "",
                                          "fallback_mode": "do_not_replace",

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
                          profile=profile,
                          report=[
                              {

                                  'field': 'favourite_singer',
                                  'rule': 'String',
                                  'number_records': 2,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [[None, None],
                                         [None, None]],

                              },
                          ])

    def test_lookup_FpCSVEncodingError(self):
        self._test_filter(dirty_file="lookup/test_cities_dirty_windows1252.csv",
                          clean_file="lookup/test_cities_dirty_windows1252_deleted.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "remove_record",
                                          "lookalike_match": False,
                                          "original_reference": "lookup/test_cities_reference1252.csv",

                                          "reference_field": "-1",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "1"
                                  }
                              ]
                          },
                          expected_error=FpCSVEncodingError,
                          report=[
                              {

                                  'field': 'favourite_singer',
                                  'rule': 'String',
                                  'number_records': 2,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [[None, None],
                                         [None, None]],

                              },
                          ])

    def test_lookup_1252(self):
        self._test_filter(dirty_file="lookup/test_cities_dirty_windows1252.csv",
                          clean_file="lookup/test_cities_dirty_windows1252_deleted.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "remove_record",
                                          "lookalike_match": False,
                                          "original_reference": "lookup/test_cities_reference1252.csv",

                                          "reference_field": "-1",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "1"
                                  }
                              ]
                          },
                          csv_encoding="Windows-1252",
                          report=[
                              {

                                  'field': 'city',
                                  'rule': 'Lookup',
                                  'number_records': 25,
                                  'category': 'replaced',
                                  'description': 'Best match',
                                  'df': [['Bsitrol', 'Bristol'],
                                         ['London', 'Croydon'],
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
                                         ['London', 'Croydon'],
                                         ['London', 'Croydon']],

                              },
                              {

                                  'field': 'city',
                                  'rule': 'Lookup',
                                  'number_records': 3,
                                  'category': 'quarantined',
                                  'description': 'Data quarantined',
                                  'df': [['Bath'],
                                         ['Btha'],
                                         ['Lndon']],

                              },
                          ])
