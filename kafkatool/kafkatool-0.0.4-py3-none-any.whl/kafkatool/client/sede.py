#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time   : 2018/12/21 5:02 PM 
# @Author : xbzheng

import json


def str_ser(data, encoding='utf8'):
    return data.encode(encoding)


def str_der(bytes_data, encoding='utf8'):
    return bytes_data.decode(encoding)


def json_ser(json_data, encoding='utf8'):
    return json.dumps(json_data, ensure_ascii=False).encode(encoding)


def json_der(bytes_data, encoding='utf8'):
    return json.loads(bytes_data, encoding=encoding)
