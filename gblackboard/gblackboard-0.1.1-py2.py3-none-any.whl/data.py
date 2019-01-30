# -*- coding: utf-8 -*-

import json

from .exception import *


class DataType:
    """
    Supported data types: integer, floating number, string and dictionary.
    """
    NONE = 0
    INT = 1
    FLOAT = 2
    STR = 3
    DICT = 4


class Data(object):

    """
    Medium `data structure` to save a value to blackboard. When a value is given, this class object check whether the
    value is list or not and what type it is and save them as member variables. This is used for transforming data
    to save to and load from blackboard.

    :param value: The data you want to store.
    :type value: int, int[], float, float[], str, str[], dict or dict[]

    :raises gblackboard.NoSupportDataType: the type of value should be one of
                                           (int, int[], float, float[], str, str[]). Especially, a list value cannot
                                           have homogeneous types.
    """

    def __init__(self, value=None):
        # initialize member variables
        self._value = None
        self._is_list = False
        self._data_type = DataType.NONE
        # restructure the value
        if value:
            self._restructure(value)

    @property
    def r_data(self):
        return {
            'list': self._is_list,
            'type': self._data_type,
            'value': self._value
        }

    @property
    def value(self):
        return self._value

    def load(self, data):
        self._is_list = data['list']
        self._data_type = data['type']
        if self._is_list:
            if self._data_type == DataType.INT:
                self._value = [int(e) for e in data['value']]
            elif self._data_type == DataType.FLOAT:
                self._value = [float(e) for e in data['value']]
            elif self._data_type == DataType.STR:
                self._value = [str(e) for e in data['value']]
            elif self._data_type == DataType.DICT:
                self._value = data['value']
            else:
                self._value = None
                raise UnsupportedDataType("Not supported data structure is given: {}".format(data))
        else:
            if self._data_type == DataType.INT:
                self._value = int(data['value'])
            elif self._data_type == DataType.FLOAT:
                self._value = float(data['value'])
            elif self._data_type == DataType.STR:
                self._value = str(data['value'])
            elif self._data_type == DataType.DICT:
                self._value = data['value']
            else:
                self._value = None
                raise UnsupportedDataType("Not supported data structure is given: {}".format(data))

    def _restructure(self, value):
        if isinstance(value, list):
            self._is_list = True
            if all(isinstance(e, int) for e in value):
                self._data_type = DataType.INT
            elif all(isinstance(e, float) for e in value):
                self._data_type = DataType.FLOAT
            elif all(isinstance(e, str) for e in value):
                self._data_type = DataType.STR
            elif all(isinstance(e, dict) for e in value):
                self._data_type = DataType.DICT
            else:
                self._is_list = False
                self._data_type = DataType.NONE
                raise UnsupportedDataType("Not supported type data is given: {}".format(value))
        else:
            self._is_list = False
            if isinstance(value, int):
                self._data_type = DataType.INT
            elif isinstance(value, float):
                self._data_type = DataType.FLOAT
            elif isinstance(value, str):
                self._data_type = DataType.STR
            elif isinstance(value, dict):
                self._data_type = DataType.DICT
            else:
                self._is_list = False
                self._data_type = DataType.NONE
                raise UnsupportedDataType("Not supported type data is given: {}".format(value))
        self._value = value

