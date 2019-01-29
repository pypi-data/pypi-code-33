# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from dativa.scrubber.tests import _BaseTest
from dativa.scrubber import ScrubberError


class DuplicationTests(_BaseTest):

    def test_duplication(self):
        self._test_filter(dirty_file="unique/duplication_test.csv",
                          clean_file="unique/duplication_test_first_col.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "Column1",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Column1',
                                  'rule': 'Uniqueness',
                                  'number_records': 2,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['A', 2],
                                         ['D', 4]],

                              },
                          ])

    def test_duplication_1(self):
        self._test_filter(dirty_file="unique/duplication_test.csv",
                          clean_file="unique/duplication_test_other_col.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "Column2",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Column2',
                                  'rule': 'Uniqueness',
                                  'number_records': 2,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['C', 3],
                                         ['D', 4]],

                              },
                          ])

    def test_duplication_2(self):
        self._test_filter(dirty_file="unique/duplication_test.csv",
                          clean_file="unique/duplication_test_all_cols.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "Column1,Column2",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Column1,Column2',
                                  'rule': 'Uniqueness',
                                  'number_records': 1,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['D', 4]],

                              },
                          ])

    def test_duplication_3(self):
        self._test_filter(dirty_file="unique/duplication_test.csv",
                          clean_file="unique/duplication_test_first_col_last.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "Column1",
                                          "use_last_value": True
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Column1',
                                  'rule': 'Uniqueness',
                                  'number_records': 2,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['A', 1],
                                         ['D', 4]],

                              },
                          ])

    def test_duplication_4(self):
        self._test_filter(dirty_file="unique/duplication_test.csv",
                          clean_file="unique/duplication_test_all_cols.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "Column1,Column2",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Column1,Column2',
                                  'rule': 'Uniqueness',
                                  'number_records': 1,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['D', 4]],

                              },
                          ])

    def test_duplication_5(self):
        self._test_filter(dirty_file="unique/duplication_test.csv",
                          clean_file="unique/duplication_test_first_col.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "Column1",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Column1',
                                  'rule': 'Uniqueness',
                                  'number_records': 2,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['A', 2],
                                         ['D', 4]],

                              },
                          ])

    def test_duplication_6(self):
        self._test_filter(dirty_file="unique/names_blank.csv",
                          clean_file="unique/names_blank_skip.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "Name",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          report=[
                              {

                                  'field': 'Name',
                                  'rule': 'Uniqueness',
                                  'number_records': 2,
                                  'category': 'quarantined',
                                  'description': 'Removed duplicates',
                                  'df': [['Sarvesh'],
                                         ['Sarvesh']],

                              },
                          ])

    def test_duplication_error(self):
        self._test_filter(dirty_file="unique/names_blank.csv",
                          clean_file="unique/names_blank_skip.csv",
                          config={
                              "rules": [
                                  {
                                      "rule_type": "Uniqueness",
                                      "params": {
                                          "unique_fields": "Donut",
                                          "use_last_value": False
                                      },
                                  }
                              ]
                          },
                          expected_error=ScrubberError)
