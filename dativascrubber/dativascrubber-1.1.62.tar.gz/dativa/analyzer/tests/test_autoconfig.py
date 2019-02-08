import unittest
import logging
from os import path
import pandas as pd
from collections import OrderedDict
import json
from dativa.tools.pandas import CSVHandler
from dativa.scrubber import DefaultProfile
from dativa.analyzer import AutoConfig

logger = logging.getLogger("dativa.analyzer.tests")


def _compare_objects(new_object, original_object, ignore_list=[]):
    if original_object is None:
        return new_object, None
    if new_object is None:
        return original_object, None
    for key in original_object:
        if key not in ignore_list:
            if key in new_object:
                if type(original_object[key]) == dict or type(original_object[key]) == OrderedDict:
                    a, b = _compare_objects(
                        new_object[key], original_object[key], ignore_list)
                    if a != b:
                        return a, b
                elif type(original_object[key]) == list:
                    for index in range(0, len(original_object[key])):
                        a, b = _compare_objects(
                            new_object[key][index], original_object[key][index], ignore_list)
                        if a != b:
                            return a, b
                elif type(original_object[key]) == tuple:
                    # skip tuples
                    pass
                elif original_object[key] is None:
                    return key, None
                else:
                    if json.dumps(original_object[key], sort_keys=True) != json.dumps(new_object[key], sort_keys=True):
                        return json.dumps("{0}: {1}".format(key, original_object[key]), sort_keys=True), json.dumps(
                            "{0}: {1}".format(key, new_object[key]), sort_keys=True)
            else:
                return key, None

    return True, True


def compare_objects(new_object, original_object, ignore_list=[]):
    a, b = _compare_objects(new_object, original_object, ignore_list)
    if a is True and b is True:
        return _compare_objects(original_object, new_object, ignore_list)
    else:
        return a, b


class AutoConfigTests(unittest.TestCase):

    def setUp(self):
        self.base_path = "{0}/test-data/analyzer/".format(
            path.dirname(path.abspath(__file__)))
        self.csv = CSVHandler(base_path=self.base_path)
        super(AutoConfigTests, self).setUp()

    def _test(self, file, config, description, iteration=10, profile=None):
        """
        Iterative test that will run up to five times to check for success.
        This is because the tests are not-deterministic due to the pandas
        sampling approach
        """
        df = self.csv.get_dataframe(file, force_dtype=pd.np.str)

        ac = AutoConfig()

        auto_config, df_dict = ac.create_config(df, profile)

        a, b = compare_objects(auto_config, config)

        if a != b and iteration > 0:
            logger.debug(
                "executed iteration #{iteration}, re-running".format(iteration=11 - iteration))
            self._test(file, config, description, iteration - 1)
            return
        if a != b:
            import pdb;
            pdb.set_trace()
        self.assertEquals(a, b)

        if description != ac.describe_dataframe(auto_config, df_dict):
            self.assertEquals(
                description, ac.describe_dataframe(auto_config, df_dict))

    def test_autoplan_blank_test(self):

        config = {"rules": [{
            "field": "word",
            "rule_type": "String",
            "params": {
                "minimum_length": 1,
                "maximum_length": 10,
                "fallback_mode": "use_default",
                "default_value": "",
                "skip_blank": True,
                "is_unique": True}},
            {"field": "number",
             "rule_type": "Number",
             "params": {
                 "minimum_value": 0,
                 "maximum_value": 0,
                 "decimal_places": 0,
                 "fix_decimal_places": True,
                 "fallback_mode": "remove_record"
             }}]}

        description = "column,type,minimum,maximum,format,has_blanks\n" + \
                      "word,String,1,10,,True\n" + \
                      "number,Number,0,0,int,False\n\n"

        self._test("blank_test.csv", config,
                   description, profile=DefaultProfile())

    def test_autoplan_blank_dirty(self):

        config = {"rules":
                      [{"field": "word",
                        "rule_type": "String",
                        "params": {
                            "minimum_length": 1,
                            "maximum_length": 10,
                            "fallback_mode": "use_default",
                            "skip_blank": True,
                            "default_value": "",
                            "skip_blank": True}},
                       {"field": "number",
                        "rule_type": "Number",
                        "params": {
                            "minimum_value": 0,
                            "maximum_value": 0,
                            "decimal_places": 0,
                            "fix_decimal_places": True,
                            "fallback_mode": "remove_record",
                            "skip_blank": True
                        }}]}

        description = "column,type,minimum,maximum,format,has_blanks\n" + \
                      "word,String,1,10,,True\n" + \
                      "number,Number,0,0,int,True\n\n"

        self._test("blank_dirty.csv", config, description)

    def test_autoplan_cities(self):
        config = {"rules": [{
            "field": "id",
            "rule_type": "Number",
            "params": {
                "minimum_value": 1,
                "maximum_value": 10,
                "decimal_places": 0,
                "fix_decimal_places": True,
                "fallback_mode": "remove_record",
                "is_unique": True}},
            {"field": "city",
             "rule_type": "String",
             "params": {
                 "minimum_length": 0,
                 "maximum_length": 10,
                 "fallback_mode": "use_default",
                 "default_value": "Bath",
                 "is_unique": True}}]}

        description = "column,type,minimum,maximum,format,has_blanks\n" + \
                      "id,Number,1,10,int,False\n" + \
                      "city,String,0,10,,False\n\n"

        self._test("test_cities_dirty.csv", config, description)

    def test_positive_dirty(self):

        config = {"rules": [{
            "field": "Column1",
            "rule_type": "Number",
            "params": {
                "minimum_value": 0,
                "maximum_value": 10,
                "decimal_places": 0,
                "fix_decimal_places": True,
                "fallback_mode": "remove_record"}},
            {"field": "Column2",
             "rule_type": "Number",
             "params": {
                 "minimum_value": 1,
                 "maximum_value": 10,
                 "decimal_places": 0,
                 "fix_decimal_places": True,
                 "fallback_mode": "remove_record"
             }}]}

        description = "column,type,minimum,maximum,format,has_blanks\n" + \
                      "Column1,Number,0,10,int,False\n" + \
                      "Column2,Number,1,10,int,False\n\n"

        self._test("positive_dirty.csv", config, description)

    def test_autoplan_fridge(self):

        config = {"rules": [{
            "field": "device_id",
            "rule_type": "Number",
            "params": {
                "minimum_value": 1000,
                "maximum_value": 20000000,
                "decimal_places": 0,
                "fix_decimal_places": True,
                "fallback_mode": "remove_record"}},
            {"field": "session_start",
             "rule_type": "Date",
             "params": {
                 "date_format": "%d/%m/%Y %H:%M",
                 'range_check': 'fixed',
                 "range_minimum": "01/01/2016 00:00",
                 "range_maximum": "31/12/2016 23:59",
                 "fallback_mode": "remove_record"}},
            {"field": "session_stop",
             "rule_type": "Date",
             "params": {
                 "date_format": "%d/%m/%Y %H:%M",
                 'range_check': 'fixed',
                 "range_minimum": "01/01/2016 00:00",
                 "range_maximum": "31/12/2016 23:59",
                 "fallback_mode": "remove_record"}},
            {"field": "average_temperature",
             "rule_type": "Number",
             "params": {
                 "decimal_places": 2,
                 "fix_decimal_places": True,
                 "minimum_value": 1,
                 "maximum_value": 10,
                 "decimal_places": 2,
                 "fix_decimal_places": True,
                 "fallback_mode": "remove_record"}},
            {"rule_type": "Uniqueness",
             "params": {
                 "unique_fields": "device_id,session_start",
                 "use_last_value": True}},
            {"rule_type": "Session",
             "params": {
                 "key_field": "device_id",
                 "start_field": "session_start",
                 "end_field": "session_stop",
                 "gaps_option": "extend_end",
                 "overlaps_option": "truncate_end",
                 "date_format": "%d/%m/%Y %H:%M"
             }}]}

        description = "column,type,minimum,maximum,format,has_blanks\n" + \
                      "device_id,Number,1000,20000000,int,False\n" + \
                      "session_start,Date,01/01/2016 00:00,31/12/2016 23:59,%d/%m/%Y %H:%M,False\n" + \
                      "session_stop,Date,01/01/2016 00:00,31/12/2016 23:59,%d/%m/%Y %H:%M,False\n" + \
                      "average_temperature,Number,1,10,0.00,False\n" + \
                      "\n" + \
                      "Unique on device_id,session_start\n" + \
                      "Session rule on session_start, session_stop with unique id device_id\n"

        self._test("fridge-test-small.csv", config, description)

    def test_session_checking(self):

        config = {
            "rules": [
                {
                    "field": "Channel",
                    "rule_type": "String",
                    "params": {
                        "minimum_length": 1,
                        "maximum_length": 10,
                        'fallback_mode': 'remove_record',
                        'regex': 'HBO'
                    }
                },
                {
                    "field": "Show",
                    "rule_type": "String",
                    "params": {
                        "minimum_length": 0,
                        "maximum_length": 20,
                        "fallback_mode": "use_default",
                        "default_value": "Game of Thrones"
                    }
                },
                {
                    "field": "Start",
                    "rule_type": "Date",
                    "params": {
                        "date_format": "%Y-%m-%d %H:%M:%S",
                        'range_check': 'fixed',
                        "range_minimum": "2016-12-01 00:00:00",
                        "range_maximum": "2016-12-01 23:59:59",
                        "fallback_mode": "remove_record",
                        "is_unique": True
                    }
                },
                {
                    "field": "Stop",
                    "rule_type": "Date",
                    "params": {
                        "date_format": "%Y-%m-%d %H:%M:%S",
                        'range_check': 'fixed',
                        "range_minimum": "2016-12-01 00:00:00",
                        "range_maximum": "2016-12-01 23:59:59",
                        "fallback_mode": "remove_record"
                    }
                },
                {
                    "rule_type": "Session",
                    "params": {
                        "key_field": "Show",
                        "start_field": "Start",
                        "end_field": "Stop",
                        "gaps_option": "ignore",
                        "overlaps_option": "truncate_end",
                        "date_format": "%Y-%m-%d %H:%M:%S"
                    }
                }
            ]
        }

        description = "column,type,minimum,maximum,format,has_blanks\n" + \
                      "Channel,String,1,10,,False\n" + \
                      "Show,String,0,20,,False\n" + \
                      "Start,Date,2016-12-01 00:00:00,2016-12-01 23:59:59,%Y-%m-%d %H:%M:%S,False\n" + \
                      "Stop,Date,2016-12-01 00:00:00,2016-12-01 23:59:59,%Y-%m-%d %H:%M:%S,False\n" + \
                      "\n" + \
                      "Session rule on Start, Stop with unique id Show\n"

        self._test("session_checking.csv", config, description)

    def test_epg(self):

        config = {
            'rules': [
                {'field': 'station_name',
                 'rule_type': 'Lookup',
                 'params': {
                     'original_reference': 'station_name.ref.csv',
                     'reference_field': 0,
                     'attempt_closest_match': True,
                     'fallback_mode': 'remove_record'}},
                {'field': 'airdate',
                 'rule_type': 'Date',
                 'params': {
                     'date_format': '%Y-%m-%d %H:%M:%S',
                     'range_check': 'fixed',
                     'range_minimum': '2017-01-01 00:00:00',
                     'range_maximum': '2017-02-28 23:59:59',
                     'fallback_mode': 'remove_record'}},
                {'field': 'title',
                 'rule_type': 'String',
                 'params': {
                     'minimum_length': 1,
                     'maximum_length': 100,
                     'fallback_mode': 'remove_record'}},
                {'field': 'epi_num',
                 'rule_type': 'String',
                 'params': {
                     'minimum_length': 1,
                     'maximum_length': 10,
                     'fallback_mode': 'use_default',
                     'skip_blank': True,
                     'default_value': ''}},
                {'field': 'epi_title',
                 'rule_type': 'String',
                 'params': {
                     'minimum_length': 1,
                     'maximum_length': 200,
                     'fallback_mode': 'use_default',
                     'skip_blank': True,
                     'default_value': ''}},
                {'field': 'genre',
                 'rule_type': 'String',
                 'params': {
                     'minimum_length': 1,
                     'maximum_length': 100,
                     'fallback_mode': 'remove_record'}},
                {'field': 'year',
                 'rule_type': 'Number',
                 'params': {
                     'decimal_places': 0,
                     'fix_decimal_places': True,
                     'minimum_value': 1000,
                     'maximum_value': 3000,
                     'fallback_mode': 'remove_record',
                     'skip_blank': True}},
                {'field': 'language',
                 'rule_type': 'String',
                 'params': {
                     'minimum_length': 0,
                     'maximum_length': 10,
                     'fallback_mode': 'remove_record',
                     'regex': 'English|Spanish'}},
                {'field': 'country_name',
                 'rule_type': 'Lookup',
                 'params': {
                     'original_reference': 'country_name.ref.csv',
                     'reference_field': 0,
                     'attempt_closest_match': True,
                     'fallback_mode': 'remove_record',
                     'skip_blank': True}},
                {'rule_type': 'Uniqueness',
                 'params': {
                     'unique_fields': 'station_name,airdate',
                     'use_last_value': True}}]}

        description = "column,type,minimum,maximum,format,has_blanks\n" + \
                      "station_name,String,A & E Network,truTV HD,Lookup,False\n" + \
                      "airdate,Date,2017-01-01 00:00:00,2017-02-28 23:59:59,%Y-%m-%d %H:%M:%S,False\n" + \
                      "title,String,1,100,,False\n" + \
                      "epi_num,String,1,10,,True\n" + \
                      "epi_title,String,1,200,,True\n" + \
                      "genre,String,1,100,,False\n" + \
                      "year,Number,1000,3000,int,True\n" + \
                      "language,String,0,10,,False\n" + \
                      "country_name,String,AUS/TUR/USA,ZAF/USA,Lookup,True\n" + \
                      "\n" + \
                      "Unique on station_name,airdate\n"

        self._test("epg-jan-2017.csv", config, description)
