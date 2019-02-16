# -*- coding: utf-8 -*-

"""Tests for `gblackboard` package."""

import unittest

from gblackboard.wrapper import DictionaryWrapper


class TestDictionaryWrapper(unittest.TestCase):
    """Tests for `gblackboard` package."""

    def setUp(self):
        self.dict_wrapper = DictionaryWrapper()

    def tearDown(self):
        self.dict_wrapper.close()

    def test_str_setter_getter(self):
        _test_str_data_key = 'str_data_key'
        _test_str_data_val = 'str_data'
        self.dict_wrapper.set(_test_str_data_key, _test_str_data_val)
        test_data = self.dict_wrapper.get(_test_str_data_key)
        self.assertEqual(test_data, _test_str_data_val)

    def test_int_setter_getter(self):
        _test_int_data_key = 'int_data_key'
        _test_int_data_val = 100
        self.dict_wrapper.set(_test_int_data_key, _test_int_data_val)
        test_data = self.dict_wrapper.get(_test_int_data_key)
        self.assertEqual(test_data, _test_int_data_val)

    def test_float_setter_getter(self):
        _test_float_data_key = 'float_data_key'
        _test_float_data_val = 0.123
        self.dict_wrapper.set(_test_float_data_key, _test_float_data_val)
        test_data = self.dict_wrapper.get(_test_float_data_key)
        self.assertEqual(test_data, _test_float_data_val)

    def test_dict_setter_getter(self):
        _test_dict_data_key = 'dict_data_key'
        _test_dict_data_val = dict(a=1, b=0.5, c='hello')
        self.dict_wrapper.set(_test_dict_data_key, _test_dict_data_val)
        test_data = self.dict_wrapper.get(_test_dict_data_key)
        self.assertDictEqual(test_data, _test_dict_data_val)

    def test_str_list_setter_getter(self):
        _test_str_list_data_key = 'str_list_data_key'
        _test_str_list_data_val = ['str0', 'str1', 'str2']
        self.dict_wrapper.set(_test_str_list_data_key, _test_str_list_data_val)
        test_data = self.dict_wrapper.get(_test_str_list_data_key)
        self.assertListEqual(test_data, _test_str_list_data_val)

    def test_int_list_setter_getter(self):
        _test_int_list_data_key = 'int_list_data_key'
        _test_int_list_data_val = [0, 1, 2]
        self.dict_wrapper.set(_test_int_list_data_key, _test_int_list_data_val)
        test_data = self.dict_wrapper.get(_test_int_list_data_key)
        self.assertListEqual(test_data, _test_int_list_data_val)

    def test_float_list_setter_getter(self):
        _test_float_list_data_key = 'float_list_data_key'
        _test_float_list_data_val = [0.123, 1.123, 2.123]
        self.dict_wrapper.set(_test_float_list_data_key, _test_float_list_data_val)
        test_data = self.dict_wrapper.get(_test_float_list_data_key)
        self.assertListEqual(test_data, _test_float_list_data_val)

    def test_dict_list_setter_getter(self):
        _test_dict_list_data_key = 'dict_list_data_key'
        _test_dict_list_data_val = [
            dict(a=1, b=0.5, c='hello world!'),
            dict(a=2, b=3.0, c='hello blackboard'),
            dict(a=100, b=45.4, c='i\'m monster')
        ]
        self.dict_wrapper.set(_test_dict_list_data_key, _test_dict_list_data_val)
        test_data = self.dict_wrapper.get(_test_dict_list_data_key)
        self.assertListEqual(test_data, _test_dict_list_data_val)


if __name__ == '__main__':
    unittest.main()
