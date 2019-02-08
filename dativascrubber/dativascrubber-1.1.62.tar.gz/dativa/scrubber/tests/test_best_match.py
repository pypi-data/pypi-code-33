# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from dativa.scrubber.tests import _BaseTest


class BestMatchTests(_BaseTest):

    def test_best_match(self):
        self._test_filter(dirty_file="generic/US1_movies_dirty.csv",
                          clean_file="generic/US1_movies_clean.csv",
                          config={
                              "rules": [
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "N/A",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/TV_Titles_Master_50000_records.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "0"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "N/A",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/TV_Titles_Master_50000_records.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "1"
                                  },
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
                                          "regex": "^0$",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "String",
                                      "field": "2"
                                  },
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
                                      "field": "3"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/Genres_Master.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "7"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/Genres_Master.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "8"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/Genres_Master.csv",
                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "9"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/Genres_Master.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "10"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/Genres_Master.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "11"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/Genres_Master.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "12"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/Genres_Master.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "13"
                                  },
                                  {
                                      "append_results": False,
                                      "params": {
                                          "attempt_closest_match": True,
                                          "default_value": "BaNonea",
                                          "fallback_mode": "do_not_replace",
                                          "lookalike_match": False,
                                          "original_reference": "generic/Genres_Master.csv",

                                          "reference_field": "0",
                                          "skip_blank": False,
                                          "string_distance_threshold": 0.7
                                      },
                                      "rule_type": "Lookup",
                                      "field": "14"
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'GroupTitle',
                                  'rule': 'Lookup',
                                  'number_records': 16,
                                  'category': 'replaced',
                                  'description': 'Best match',
                                  'df': [['Escape from L.A.', 'Escape from LA'],
                                         ['Executioners From Shaolin', 'Executed'],
                                         ['Five Shaolin Masters', 'Five Fingers'],
                                         ['Hungry for Change', 'Chor Aur Chand'],
                                         ['Invincible Shaolin', 'In Her Shoes'],
                                         ['Killer Legends', 'Beast Legends'],
                                         ['Knockout', 'AM Workout'],
                                         ['Nick of Time', 'Dick Tiger'],
                                         ['Pulp Fiction', 'Am Politician'],
                                         ['Reservoir Dogs', 'Firehouse Dog'],
                                         ['Soaked in Bleach', 'A Second Chance'],
                                         ['Survivor', 'Aurora'],
                                         ['The Truman Show', 'Fred The Show'],
                                         ['The Warriors', 'Fish Warrior'],
                                         ['Upstream Color', "Ceart's Coir"],
                                         ['Urban Cowboy', 'Carry On Cowboy']],

                              },
                              {

                                  'field': 'GroupTitle',
                                  'rule': 'Lookup',
                                  'number_records': 4,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [['Martial Arts of Shaolin', 'Martial Arts of Shaolin'],
                                         ['Return To The 36th Chamber', 'Return To The 36th Chamber'],
                                         ['The Avenging Eagle', 'The Avenging Eagle'],
                                         ['The Five Venoms', 'The Five Venoms']],

                              },
                              {

                                  'field': 'Title',
                                  'rule': 'Lookup',
                                  'number_records': 16,
                                  'category': 'replaced',
                                  'description': 'Best match',
                                  'df': [['Escape from L.A.', 'Escape from LA'],
                                         ['Executioners From Shaolin', 'Executed'],
                                         ['Five Shaolin Masters', 'Five Fingers'],
                                         ['Hungry for Change', 'Chor Aur Chand'],
                                         ['Invincible Shaolin', 'In Her Shoes'],
                                         ['Killer Legends', 'Beast Legends'],
                                         ['Knockout', 'AM Workout'],
                                         ['Nick of Time', 'Dick Tiger'],
                                         ['Pulp Fiction', 'Am Politician'],
                                         ['Reservoir Dogs', 'Firehouse Dog'],
                                         ['Soaked in Bleach', 'A Second Chance'],
                                         ['Survivor', 'Aurora'],
                                         ['The Truman Show', 'Fred The Show'],
                                         ['The Warriors', 'Fish Warrior'],
                                         ['Upstream Color', "Ceart's Coir"],
                                         ['Urban Cowboy', 'Carry On Cowboy']],

                              },
                              {

                                  'field': 'Title',
                                  'rule': 'Lookup',
                                  'number_records': 4,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [['Martial Arts of Shaolin', 'Martial Arts of Shaolin'],
                                         ['Return To The 36th Chamber', 'Return To The 36th Chamber'],
                                         ['The Avenging Eagle', 'The Avenging Eagle'],
                                         ['The Five Venoms', 'The Five Venoms']],

                              },
                              {

                                  'field': 'Genre2',
                                  'rule': 'Lookup',
                                  'number_records': 24,
                                  'category': 'replaced',
                                  'description': 'Best match',
                                  'df': [[' Adventures', 'Adventures'],
                                         [' Action Thrillers', 'Action Thrillers'],
                                         [' Action Thrillers', 'Action Thrillers'],
                                         [' Supernatural Horror Films', 'Supernatural Horror Films'],
                                         [' International Action & Adventure',
                                          'International Action & Adventure'],
                                         [' International Action & Adventure',
                                          'International Action & Adventure'],
                                         [' Social & Cultural Documentaries',
                                          'Social & Cultural Documentaries'],
                                         [' Documentaries', 'Documentaries'],
                                         [' International Action & Adventure',
                                          'International Action & Adventure'],
                                         [' Crime Documentaries', 'Crime Documentaries'],
                                         [' Films for ages 8 to 10', 'Films for ages 8 to 10'],
                                         [' International Action & Adventure',
                                          'International Action & Adventure'],
                                         [' Crime Thrillers', 'Crime Thrillers'],
                                         [' Crime Dramas', 'Crime Dramas'],
                                         [' Thrillers', 'Thrillers'],
                                         [' International Action & Adventure',
                                          'International Action & Adventure'],
                                         [' Crime Documentaries', 'Crime Documentaries'],
                                         [' Action Thrillers', 'Action Thrillers'],
                                         [' International Action & Adventure',
                                          'International Action & Adventure'],
                                         [' International Action & Adventure',
                                          'International Action & Adventure'],
                                         [' Dark Comedies', 'Dark Comedies'],
                                         [' Classic Action & Adventure', 'Classic Action & Adventure'],
                                         [' Independent Dramas', 'Independent Dramas'],
                                         [' Romantic Dramas', 'Romantic Dramas']],

                              },
                              {

                                  'field': 'Genre3',
                                  'rule': 'Lookup',
                                  'number_records': 21,
                                  'category': 'replaced',
                                  'description': 'Best match',
                                  'df': [[' Thrillers', 'Thrillers'],
                                         [' Sci-Fi Thrillers', 'Sci-Fi Thrillers'],
                                         [' Cult Films', 'Cult Films'],
                                         [' Sci-Fi & Fantasy', 'Sci-Fi & Fantasy'],
                                         [' Asian Action Films', 'Asian Action Films'],
                                         [' Asian Action Films', 'Asian Action Films'],
                                         [' Social & Cultural Documentaries',
                                          'Social & Cultural Documentaries'],
                                         [' Asian Action Films', 'Asian Action Films'],
                                         [' Social & Cultural Documentaries',
                                          'Social & Cultural Documentaries'],
                                         [' Films for ages 11 to 12', 'Films for ages 11 to 12'],
                                         [' Asian Action Films', 'Asian Action Films'],
                                         [' Independent Dramas', 'Independent Dramas'],
                                         [' Crime Thrillers', 'Crime Thrillers'],
                                         [' Asian Action Films', 'Asian Action Films'],
                                         [' Spy Action & Adventure', 'Spy Action & Adventure'],
                                         [' Asian Action Films', 'Asian Action Films'],
                                         [' Asian Action Films', 'Asian Action Films'],
                                         [' Dramas', 'Dramas'],
                                         [' Action Thrillers', 'Action Thrillers'],
                                         [' Independent Films', 'Independent Films'],
                                         [' Romantic Films', 'Romantic Films']],

                              },
                              {

                                  'field': 'Genre5',
                                  'rule': 'Lookup',
                                  'number_records': 2,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [[None, None],
                                         [None, None]],

                              },
                              {

                                  'field': 'Genre6',
                                  'rule': 'Lookup',
                                  'number_records': 4,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [[None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None]],

                              },
                              {

                                  'field': 'Genre7',
                                  'rule': 'Lookup',
                                  'number_records': 11,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [[None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None]],

                              },
                              {

                                  'field': 'Genre8',
                                  'rule': 'Lookup',
                                  'number_records': 20,
                                  'category': 'ignored',
                                  'description': 'No changes made',
                                  'df': [[None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None],
                                         [None, None]],

                              },
                          ])
