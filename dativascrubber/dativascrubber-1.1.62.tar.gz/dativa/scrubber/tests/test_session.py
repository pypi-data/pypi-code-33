# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from datetime import datetime
from dativa.tools.pandas import CSVHandler
from dativa.scrubber.tests import _BaseTest
from dativa.scrubber.validators import SessionValidator


def _to_time(a):
    return datetime.strptime(a, '%Y-%m-%d %H:%M:%S')


class SessionTests(_BaseTest):

    def test_session_chetan(self):
        self._test_filter(dirty_file="session/session_check.csv",
                          clean_file="session/session_check_cleaned.csv",
                          config={"rules": [{
                              "rule_type": "Session",
                              "params": {
                                  "template_for_new": "Channel, test1, Start, Stop",
                                  "overlaps_option": "truncate_start",
                                  "key_field": "Channel",
                                  "start_field": "Start",
                                  "date_format": "%Y-%m-%d %H:%M:%S",
                                  "gaps_option": "insert_new",
                                  "end_field": "Stop"}}]},
                          report=[
                              {

                                  'field': 'Start',
                                  'rule': 'Session',
                                  'number_records': 2,
                                  'category': 'modified',
                                  'description': 'Truncated start',
                                  'df': [['HBO', '2016-12-01 18:00:54', '2016-12-01 18:01:10',
                                          _to_time('2016-12-01 18:00:59')],
                                         ['HBO', '2016-12-01 18:00:55', '2016-12-01 18:01:11',
                                          _to_time('2016-12-01 18:01:10')]],

                              },
                              {

                                  'field': 'Start',
                                  'rule': 'Session',
                                  'number_records': 3,
                                  'category': 'inserted',
                                  'description': 'Filled gaps',
                                  'df': [['HBO', '2016-12-01 13:30:00', '2016-12-01 13:31:00'],
                                         ['HBO', '2016-12-01 16:05:00', '2016-12-01 16:05:06'],
                                         ['HBO', '2016-12-01 17:00:00', '2016-12-01 17:00:01']],

                              },
                          ])

    def test_sessiontest_session_(self):
        self._test_filter(dirty_file="session/check_epoch_time.csv",
                          clean_file="session/check_epoch_time_cleaned.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%s",
                                      "end_field": "utc_air_stop_epoch",
                                      "gaps_option": "extend_start",

                                      "key_field": "local_tz_offset",
                                      "overlaps_option": "truncate_start",
                                      "remove_zero_length": False,
                                      "start_field": "utc_air_start_epoch",
                                      "template_for_new": "14400,1511315524,1511315554"
                                  },
                              }]
                          }
                          ,
                          report=[
                              {

                                  'field': 'utc_air_start_epoch',
                                  'rule': 'Session',
                                  'number_records': 21,
                                  'category': 'modified',
                                  'description': 'Extended start',
                                  'df': [[14400, 1511315524, 1511315554, _to_time('2017-11-22 01:32:34')],
                                         [14400, 1511322169, 1511322199, _to_time('2017-11-22 01:52:34')],
                                         [14400, 1511328724, 1511328754, _to_time('2017-11-22 03:43:19')],
                                         [14400, 1511329924, 1511329954, _to_time('2017-11-22 05:32:34')],
                                         [14400, 1511336569, 1511336599, _to_time('2017-11-22 05:52:34')],
                                         [14400, 1511343124, 1511343154, _to_time('2017-11-22 07:43:19')],
                                         [14400, 1511344324, 1511344354, _to_time('2017-11-22 09:32:34')],
                                         [14400, 1511350969, 1511350999, _to_time('2017-11-22 09:52:34')],
                                         [14400, 1511357524, 1511357554, _to_time('2017-11-22 11:43:19')],
                                         [14400, 1511358724, 1511358754, _to_time('2017-11-22 13:32:34')],
                                         [14400, 1511365369, 1511365399, _to_time('2017-11-22 13:52:34')],
                                         [14400, 1511371924, 1511371954, _to_time('2017-11-22 15:43:19')],
                                         [14400, 1511372599, 1511372634, _to_time('2017-11-22 17:32:34')],
                                         [14400, 1511373124, 1511373154, _to_time('2017-11-22 17:43:54')],
                                         [14400, 1511373354, 1511373419, _to_time('2017-11-22 17:52:34')],
                                         [14400, 1511378809, 1511378844, _to_time('2017-11-22 17:56:59')],
                                         [14400, 1511379769, 1511379799, _to_time('2017-11-22 19:27:24')],
                                         [14400, 1511386009, 1511386044, _to_time('2017-11-22 19:43:54')],
                                         [14400, 1511386999, 1511387034, _to_time('2017-11-22 21:27:24')],
                                         [14400, 1511393209, 1511393244, _to_time('2017-11-22 21:43:54')],
                                         [14400, 1511394199, 1511394234, _to_time('2017-11-22 23:27:24')]],

                              }
                          ])

    def test_session_1(self):
        self._test_filter(dirty_file="session/check_epoch_time.csv",
                          clean_file="session/check_epoch_time_cleaned.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%s",
                                      "end_field": "utc_air_stop_epoch",
                                      "gaps_option": "extend_start",

                                      "key_field": "local_tz_offset",
                                      "overlaps_option": "truncate_start",
                                      "remove_zero_length": False,
                                      "start_field": "utc_air_start_epoch",
                                      "template_for_new": "14400,1511315524,1511315554"
                                  },
                              }, {
                                  "rule_type": "String",
                                  "field": "utc_air_start_epoch",
                                  "append_results": False,
                                  "params": {
                                      "attempt_closest_match": False,
                                      "default_value": "N/A",
                                      "fallback_mode": "use_default",

                                      "is_unique": False,
                                      "lookalike_match": False,
                                      "maximum_length": 20,
                                      "minimum_length": 0,
                                      "regex": ".*",
                                      "skip_blank": False,
                                      "string_distance_threshold": 0.7
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'utc_air_start_epoch',
                                  'rule': 'Session',
                                  'number_records': 21,
                                  'category': 'modified',
                                  'description': 'Extended start',
                                  'df': [[14400, 1511315524, 1511315554, _to_time('2017-11-22 01:32:34')],
                                         [14400, 1511322169, 1511322199, _to_time('2017-11-22 01:52:34')],
                                         [14400, 1511328724, 1511328754, _to_time('2017-11-22 03:43:19')],
                                         [14400, 1511329924, 1511329954, _to_time('2017-11-22 05:32:34')],
                                         [14400, 1511336569, 1511336599, _to_time('2017-11-22 05:52:34')],
                                         [14400, 1511343124, 1511343154, _to_time('2017-11-22 07:43:19')],
                                         [14400, 1511344324, 1511344354, _to_time('2017-11-22 09:32:34')],
                                         [14400, 1511350969, 1511350999, _to_time('2017-11-22 09:52:34')],
                                         [14400, 1511357524, 1511357554, _to_time('2017-11-22 11:43:19')],
                                         [14400, 1511358724, 1511358754, _to_time('2017-11-22 13:32:34')],
                                         [14400, 1511365369, 1511365399, _to_time('2017-11-22 13:52:34')],
                                         [14400, 1511371924, 1511371954, _to_time('2017-11-22 15:43:19')],
                                         [14400, 1511372599, 1511372634, _to_time('2017-11-22 17:32:34')],
                                         [14400, 1511373124, 1511373154, _to_time('2017-11-22 17:43:54')],
                                         [14400, 1511373354, 1511373419, _to_time('2017-11-22 17:52:34')],
                                         [14400, 1511378809, 1511378844, _to_time('2017-11-22 17:56:59')],
                                         [14400, 1511379769, 1511379799, _to_time('2017-11-22 19:27:24')],
                                         [14400, 1511386009, 1511386044, _to_time('2017-11-22 19:43:54')],
                                         [14400, 1511386999, 1511387034, _to_time('2017-11-22 21:27:24')],
                                         [14400, 1511393209, 1511393244, _to_time('2017-11-22 21:43:54')],
                                         [14400, 1511394199, 1511394234, _to_time('2017-11-22 23:27:24')]],

                              },
                          ])

    def test_session_2(self):
        self._test_filter(dirty_file="session/check_epoch_time.csv",
                          clean_file="session/check_epoch_time_cleaned.csv",
                          config={
                              "rules": [{
                                  "rule_type": "String",
                                  "field": "local_tz_offset",
                                  "append_results": False,
                                  "params": {
                                      "attempt_closest_match": False,
                                      "default_value": "N/A",
                                      "fallback_mode": "use_default",

                                      "is_unique": False,
                                      "lookalike_match": False,
                                      "maximum_length": 20,
                                      "minimum_length": 0,
                                      "regex": ".*",
                                      "skip_blank": False,
                                      "string_distance_threshold": 0.7
                                  },
                              }, {
                                  "rule_type": "String",
                                  "field": "utc_air_start_epoch",
                                  "append_results": False,
                                  "params": {
                                      "attempt_closest_match": False,
                                      "default_value": "N/A",
                                      "fallback_mode": "use_default",

                                      "is_unique": False,
                                      "lookalike_match": False,
                                      "maximum_length": 20,
                                      "minimum_length": 0,
                                      "regex": ".*",
                                      "skip_blank": False,
                                      "string_distance_threshold": 0.7
                                  },
                              }, {
                                  "rule_type": "String",
                                  "field": "utc_air_stop_epoch",
                                  "append_results": False,
                                  "params": {
                                      "attempt_closest_match": False,
                                      "default_value": "N/A",
                                      "fallback_mode": "use_default",

                                      "is_unique": False,
                                      "lookalike_match": False,
                                      "maximum_length": 20,
                                      "minimum_length": 0,
                                      "regex": ".*",
                                      "skip_blank": False,
                                      "string_distance_threshold": 0.7
                                  },
                              }, {
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%s",
                                      "end_field": "utc_air_stop_epoch",
                                      "gaps_option": "extend_start",

                                      "key_field": "local_tz_offset",
                                      "overlaps_option": "truncate_start",
                                      "remove_zero_length": False,
                                      "start_field": "utc_air_start_epoch",
                                      "template_for_new": "14400,1511315524,1511315554"
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'utc_air_start_epoch',
                                  'rule': 'Session',
                                  'number_records': 21,
                                  'category': 'modified',
                                  'description': 'Extended start',
                                  'df': [['14400', '1511315524', '1511315554',
                                          _to_time('2017-11-22 01:32:34')],
                                         ['14400', '1511322169', '1511322199',
                                          _to_time('2017-11-22 01:52:34')],
                                         ['14400', '1511328724', '1511328754',
                                          _to_time('2017-11-22 03:43:19')],
                                         ['14400', '1511329924', '1511329954',
                                          _to_time('2017-11-22 05:32:34')],
                                         ['14400', '1511336569', '1511336599',
                                          _to_time('2017-11-22 05:52:34')],
                                         ['14400', '1511343124', '1511343154',
                                          _to_time('2017-11-22 07:43:19')],
                                         ['14400', '1511344324', '1511344354',
                                          _to_time('2017-11-22 09:32:34')],
                                         ['14400', '1511350969', '1511350999',
                                          _to_time('2017-11-22 09:52:34')],
                                         ['14400', '1511357524', '1511357554',
                                          _to_time('2017-11-22 11:43:19')],
                                         ['14400', '1511358724', '1511358754',
                                          _to_time('2017-11-22 13:32:34')],
                                         ['14400', '1511365369', '1511365399',
                                          _to_time('2017-11-22 13:52:34')],
                                         ['14400', '1511371924', '1511371954',
                                          _to_time('2017-11-22 15:43:19')],
                                         ['14400', '1511372599', '1511372634',
                                          _to_time('2017-11-22 17:32:34')],
                                         ['14400', '1511373124', '1511373154',
                                          _to_time('2017-11-22 17:43:54')],
                                         ['14400', '1511373354', '1511373419',
                                          _to_time('2017-11-22 17:52:34')],
                                         ['14400', '1511378809', '1511378844',
                                          _to_time('2017-11-22 17:56:59')],
                                         ['14400', '1511379769', '1511379799',
                                          _to_time('2017-11-22 19:27:24')],
                                         ['14400', '1511386009', '1511386044',
                                          _to_time('2017-11-22 19:43:54')],
                                         ['14400', '1511386999', '1511387034',
                                          _to_time('2017-11-22 21:27:24')],
                                         ['14400', '1511393209', '1511393244',
                                          _to_time('2017-11-22 21:43:54')],
                                         ['14400', '1511394199', '1511394234',
                                          _to_time('2017-11-22 23:27:24')]],

                              },
                          ])

    def test_session_3(self):
        self._test_filter(dirty_file="session/check_epoch_time_threshold_dirty.csv",
                          clean_file="session/check_epoch_time_threshold_cleaned.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 1,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%s",
                                      "end_field": "2",
                                      "gaps_option": "extend_start",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_start",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'utc_air_start_epoch',
                                  'rule': 'Session',
                                  'number_records': 2,
                                  'category': 'modified',
                                  'description': 'Truncated start',
                                  'df': [[14400, 1511315524, 1511315554, _to_time('2017-11-22 23:43:54')],
                                         [14400, 1511378809, 1511378844, _to_time('2017-11-22 19:43:19')]],

                              },
                              {

                                  'field': 'utc_air_start_epoch',
                                  'rule': 'Session',
                                  'number_records': 16,
                                  'category': 'modified',
                                  'description': 'Extended start',
                                  'df': [[14400, 1511322169, 1511322199, _to_time('2017-11-22 01:52:34')],
                                         [14400, 1511328724, 1511328754, _to_time('2017-11-22 03:43:19')],
                                         [14400, 1511329924, 1511329954, _to_time('2017-11-22 05:32:34')],
                                         [14400, 1511336569, 1511336599, _to_time('2017-11-22 05:52:34')],
                                         [14400, 1511343124, 1511343154, _to_time('2017-11-22 07:43:19')],
                                         [14400, 1511344324, 1511344354, _to_time('2017-11-22 09:32:34')],
                                         [14400, 1511357524, 1511357554, _to_time('2017-11-22 09:52:34')],
                                         [14400, 1511358724, 1511358754, _to_time('2017-11-22 11:43:19')],
                                         [14400, 1511365369, 1511365399, _to_time('2017-11-22 13:52:34')],
                                         [14400, 1511371924, 1511371954, _to_time('2017-11-22 15:43:19')],
                                         [14400, 1511372599, 1511372634, _to_time('2017-11-22 17:32:34')],
                                         [14400, 1511373124, 1511373154, _to_time('2017-11-22 17:43:54')],
                                         [14400, 1511373354, 1511373419, _to_time('2017-11-22 17:52:34')],
                                         [14400, 1511386009, 1511386044, _to_time('2017-11-22 19:27:24')],
                                         [14400, 1511386999, 1511387034, _to_time('2017-11-22 19:43:54')],
                                         [14400, 1511393209, 1511393244, _to_time('2017-11-22 21:43:54')]],
                              },
                          ])

    def test_session_4(self):
        self._test_filter(dirty_file="session/check_epoch_time_insert_new_dirty1.csv",
                          clean_file="session/check_epoch_time_insert_new_cleaned1.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 1,
                                      "allowed_overlap_seconds": 2,
                                      "date_format": "%s",
                                      "end_field": "3",
                                      "gaps_option": "insert_new",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": False,
                                      "start_field": "2",
                                      "template_for_new": "local_tz_offset,program,utc_air_start_epoch,utc_air_stop_epoch"
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'utc_air_stop_epoch',
                                  'rule': 'Session',
                                  'number_records': 2,
                                  'category': 'modified',
                                  'description': 'Truncated end',
                                  'df': [[14400, 1511314356, 1511394234, _to_time('2017-11-22 01:52:04')],
                                         [14400, 1511373420, 1511379799, _to_time('2017-11-22 19:26:49')]],

                              },
                              {

                                  'field': 'utc_air_start_epoch',
                                  'rule': 'Session',
                                  'number_records': 18,
                                  'category': 'inserted',
                                  'description': 'Filled gaps',
                                  'df': [[14400, 1511314354, '1511314356'],
                                         [14400, 1511315554, '1511322169'],
                                         [14400, 1511322199, '1511328724'],
                                         [14400, 1511328754, '1511329924'],
                                         [14400, 1511329954, '1511336569'],
                                         [14400, 1511336599, '1511343124'],
                                         [14400, 1511343154, '1511344324'],
                                         [14400, 1511344354, '1511357524'],
                                         [14400, 1511357554, '1511357574'],
                                         [14400, 1511350999, '1511358724'],
                                         [14400, 1511358754, '1511365369'],
                                         [14400, 1511365399, '1511371924'],
                                         [14400, 1511371954, '1511372599'],
                                         [14400, 1511372634, '1511373124'],
                                         [14400, 1511373154, '1511373354'],
                                         [14400, 1511378844, '1511386009'],
                                         [14400, 1511379834, '1511386999'],
                                         [14400, 1511387034, '1511393209']],

                              },
                          ])

    def test_session_5(self):
        self._test_filter(dirty_file="session/gap_first_time.csv",
                          clean_file="session/clean_time.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%H:%M",
                                      "end_field": "2",
                                      "gaps_option": "extend_end",

                                      "key_field": "0",
                                      "overlaps_option": "ignore",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'stop',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Extended end',
                                  'df': [[1, '00:00', '00:30', _to_time('1900-01-01 01:00:00')]],

                              },
                          ])

    def test_session_6(self):
        self._test_filter(dirty_file="session/gap_first.csv",
                          clean_file="session/clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "extend_end",

                                      "key_field": "0",
                                      "overlaps_option": "ignore",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'stop',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Extended end',
                                  'df': [[1, '2016-11-01 00:00', '2016-11-01 00:30',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                          ])

    def test_session_7(self):
        self._test_filter(dirty_file="session/gap_second.csv",
                          clean_file="session/clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "extend_start",

                                      "key_field": "0",
                                      "overlaps_option": "ignore",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Extended start',
                                  'df': [[1, '2016-11-01 01:30', '2016-11-01 02:00',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                          ])

    def test_session_8(self):
        self._test_filter(dirty_file="session/gap_two.csv",
                          clean_file="session/clean_gap_first_insert.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "insert_new",

                                      "key_field": "0",
                                      "overlaps_option": "ignore",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": "0, 1970-01-01 00:00, 1970-01-01 00:00,X"
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 2,
                                  'category': 'inserted',
                                  'description': 'Filled gaps',
                                  'df': [[1, '2016-11-01 00:30', '2016-11-01 01:00'],
                                         [2, '2016-11-01 00:30', '2016-11-01 01:00']],

                              },
                          ])

    def test_session_9(self):
        self._test_filter(dirty_file="session/overlap_child.csv",
                          clean_file="session/clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "ignore",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_start",
                                      "remove_zero_length": True,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 2,
                                  'category': 'modified',
                                  'description': 'Truncated start',
                                  'df': [[1, '2016-11-01 00:30', '2016-11-01 02:00',
                                          _to_time('2016-11-01 01:00:00')],
                                         [1, '2016-11-01 01:00', '2016-11-01 02:00',
                                          _to_time('2016-11-01 02:00:00')]],

                              },
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'quarantined',
                                  'description': 'Removed zero length',
                                  'df': [[1, '2016-11-01 01:00', '2016-11-01 02:00']],

                              },
                          ])

    def test_session_10(self):
        self._test_filter(dirty_file="session/overlap_first.csv",
                          clean_file="session/clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "ignore",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'stop',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated end',
                                  'df': [[1, '2016-11-01 00:00', '2016-11-01 01:30',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                          ])

    def test_session_11(self):
        self._test_filter(dirty_file="session/overlap_first_2.csv",
                          clean_file="session/clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "ignore",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'stop',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated end',
                                  'df': [[1, '2016-11-01 00:00', '2016-11-01 02:00',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                          ])

    def test_session_12(self):
        self._test_filter(dirty_file="session/overlap_full.csv",
                          clean_file="session/clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "ignore",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": True,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'stop',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated end',
                                  'df': [[1, '2016-11-01 01:00', '2016-11-01 02:00',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'quarantined',
                                  'description': 'Removed zero length',
                                  'df': [[1, '2016-11-01 01:00', '2016-11-01 02:00']],

                              },
                          ])

    def test_session_13(self):
        self._test_filter(dirty_file="session/overlap_full.csv",
                          clean_file="session/clean_overlap_full_with_zero.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "ignore",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'stop',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated end',
                                  'df': [[1, '2016-11-01 01:00', '2016-11-01 02:00',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                          ])

    def test_session_14(self):
        self._test_filter(dirty_file="session/overlap_second.csv",
                          clean_file="session/clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "ignore",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_start",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated start',
                                  'df': [[1, '2016-11-01 00:30', '2016-11-01 02:00',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                          ])

    def test_session_15(self):
        self._test_filter(dirty_file="session/overlap_second_2.csv",
                          clean_file="session/clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "ignore",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_start",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated start',
                                  'df': [[1, '2016-11-01 00:00', '2016-11-01 02:00',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                          ])

    def test_session_16(self):
        self._test_filter(dirty_file="session/alternate_overlap_second.csv",
                          clean_file="session/clean_alternate.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "3",
                                      "gaps_option": "ignore",

                                      "key_field": "1",
                                      "overlaps_option": "truncate_start",
                                      "remove_zero_length": False,
                                      "start_field": "0",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated start',
                                  'df': [[1, '2016-11-01 00:30', '2016-11-01 02:00',
                                          _to_time('2016-11-01 01:00:00')]],

                              },
                          ])

    def test_session_17(self):
        self._test_filter(dirty_file="session/Session_Test1.csv",
                          clean_file="session/Session_Test_clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "3",
                                      "gaps_option": "insert_new",

                                      "key_field": "Channel",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": False,
                                      "start_field": "2",
                                      "template_for_new": "channel,show,start,stop"
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'Stop',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated end',
                                  'df': [['HBO', '2016-12-01 15:00', '2016-12-01 16:05',
                                          _to_time('2016-12-01 16:00:00')]],

                              },
                              {

                                  'field': 'Start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'inserted',
                                  'description': 'Filled gaps',
                                  'df': [['HBO', '2016-12-01 14:00', '2016-12-01 15:00']],

                              },
                          ])

    def test_session_18(self):
        self._test_filter(dirty_file="session/Session Test 2 only 2 records.csv",
                          clean_file="session/clean2.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%d/%m/%Y %H:%M",
                                      "end_field": "3",
                                      "gaps_option": "insert_new",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": True,
                                      "start_field": "2",
                                      "template_for_new": "channel, unknown program, start, stop"
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'Stop',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated end',
                                  'df': [['HBO', '01/12/2016 16:00', '01/12/2016 16:30',
                                          _to_time('2016-12-01 16:00:00')]],

                              },
                              {

                                  'field': 'Start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'quarantined',
                                  'description': 'Removed zero length',
                                  'df': [['HBO', '01/12/2016 16:00', '01/12/2016 16:30']],

                              },
                          ])

    def test_session_19(self):
        self._test_filter(dirty_file="session/allowed_gap_seconds.csv",
                          clean_file="session/clean_allowed_gap_seconds.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 1,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%d/%m/%Y %H:%M:%S",
                                      "end_field": "2",
                                      "gaps_option": "extend_start",

                                      "key_field": "0",
                                      "overlaps_option": "ignore",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'Start Date',
                                  'rule': 'Session',
                                  'number_records': 2,
                                  'category': 'modified',
                                  'description': 'Extended start',
                                  'df': [[1, '09/11/2016 23:14:09', '09/11/2016 23:14:15',
                                          _to_time('2016-11-09 23:13:27')],
                                         [1, '09/11/2016 23:14:18', '09/11/2016 23:14:20',
                                          _to_time('2016-11-09 23:14:15')]],

                              },
                          ])

    def test_session_20(self):
        self._test_filter(dirty_file="session/allowed_gap_seconds.csv",
                          clean_file="session/clean_allowed_gap_seconds1.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 1,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%d/%m/%Y %H:%M:%S",
                                      "end_field": "2",
                                      "gaps_option": "insert_new",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": False,
                                      "start_field": "1",
                                      "template_for_new": "id,Start Date,End date,skip"
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'Start Date',
                                  'rule': 'Session',
                                  'number_records': 2,
                                  'category': 'inserted',
                                  'description': 'Filled gaps',
                                  'df': [[1, '09/11/2016 23:13:27', '09/11/2016 23:14:09'],
                                         [1, '09/11/2016 23:14:15', '09/11/2016 23:14:18']],

                              },
                          ])

    def test_session_21(self):
        self._test_filter(dirty_file="session/NewSession rule checking file.csv",
                          clean_file="session/NewSession rule checking file clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 1,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%d/%m/%Y %H:%M:%S",
                                      "end_field": "3",
                                      "gaps_option": "extend_end",

                                      "key_field": "0",
                                      "overlaps_option": "ignore",
                                      "remove_zero_length": False,
                                      "start_field": "2",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'End date',
                                  'rule': 'Session',
                                  'number_records': 3,
                                  'category': 'modified',
                                  'description': 'Extended end',
                                  'df': [['ITV', '09/11/2016 23:13:21', '09/11/2016 23:13:27',
                                          _to_time('2016-11-09 23:13:30')],
                                         ['ITV', '09/11/2016 23:13:30', '09/11/2016 23:14:00',
                                          _to_time('2016-11-09 23:14:05')],
                                         ['ITV', '09/11/2016 23:14:21', '10/11/2016 23:14:40',
                                          _to_time('2016-11-11 23:14:00')]],

                              },
                          ])

    def test_session_22(self):
        self._test_filter(dirty_file="session/NewSession rule checking file.csv",
                          clean_file="session/NewSession rule checking file clean1.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 1,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%d/%m/%Y %H:%M:%S",
                                      "end_field": "3",
                                      "gaps_option": "insert_new",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": False,
                                      "start_field": "2",
                                      "template_for_new": "Channel,Program,Start Date,End date"
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'Start Date',
                                  'rule': 'Session',
                                  'number_records': 3,
                                  'category': 'inserted',
                                  'description': 'Filled gaps',
                                  'df': [['ITV', '09/11/2016 23:13:27', '09/11/2016 23:13:30'],
                                         ['ITV', '09/11/2016 23:14:00', '09/11/2016 23:14:05'],
                                         ['ITV', '10/11/2016 23:14:40', '11/11/2016 23:14:00']],

                              },
                          ])

    def test_session_23(self):
        self._test_filter(dirty_file="session/NewSession rule checking file1.csv",
                          clean_file="session/NewSession rule checking file clean2.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 1,
                                      "allowed_overlap_seconds": 2,
                                      "date_format": "%d/%m/%Y %H:%M:%S",
                                      "end_field": "3",
                                      "gaps_option": "insert_new",

                                      "key_field": "0",
                                      "overlaps_option": "truncate_end",
                                      "remove_zero_length": False,
                                      "start_field": "2",
                                      "template_for_new": "Channel,Program,Start Date,End date"
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'End date',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'modified',
                                  'description': 'Truncated end',
                                  'df': [['ITV', '11/11/2016 23:14:45', '11/11/2016 23:15:05',
                                          _to_time('2016-11-11 23:15:00')]],

                              },
                              {

                                  'field': 'Start Date',
                                  'rule': 'Session',
                                  'number_records': 2,
                                  'category': 'inserted',
                                  'description': 'Filled gaps',
                                  'df': [['ITV', '09/11/2016 23:14:00', '09/11/2016 23:14:05'],
                                         ['ITV', '10/11/2016 23:14:40', '11/11/2016 23:14:45']],

                              }])

    def test_session_just_remove_zeros(self):
        self._test_filter(dirty_file="session/clean_overlap_full_with_zero.csv",
                          clean_file="session/clean_overlap_full_with_zero_clean.csv",
                          config={
                              "rules": [{
                                  "rule_type": "Session",
                                  "params": {
                                      "allowed_gap_seconds": 0,
                                      "allowed_overlap_seconds": 0,
                                      "date_format": "%Y-%m-%d %H:%M",
                                      "end_field": "2",
                                      "gaps_option": "ignore",

                                      "key_field": "0",
                                      "overlaps_option": "ignore",
                                      "remove_zero_length": True,
                                      "start_field": "1",
                                      "template_for_new": ""
                                  },
                              }]
                          },
                          report=[
                              {

                                  'field': 'start',
                                  'rule': 'Session',
                                  'number_records': 1,
                                  'category': 'quarantined',
                                  'description': 'Removed zero length',
                                  'df': [[1, '2016-11-01 01:00', '2016-11-01 01:00']],

                              },
                          ])

    def test_session_count_good_rows(self):
        csv = CSVHandler(base_path=self.base_path)

        df = csv.get_dataframe("session/clean_overlap_full_with_zero.csv")

        validator = SessionValidator({
            "allowed_gap_seconds": 0,
            "allowed_overlap_seconds": 0,
            "date_format": "%Y-%m-%d %H:%M",
            "end_field": "2",
            "gaps_option": "ignore",
            "key_field": "0",
            "overlaps_option": "ignore",
            "remove_zero_length": True,
            "start_field": "1",
            "template_for_new": ""})

        self.assertEqual(validator.count_good_rows(df), 5)

        df = csv.get_dataframe("session/clean_overlap_full_with_zero_clean.csv")

        self.assertEqual(validator.count_good_rows(df), 4)
