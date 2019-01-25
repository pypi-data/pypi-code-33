#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      mysql_model.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    zhouqinmin(zqm175899960@163.com)
    @date:      January 23, 2019
    @desc:      MySqlModel
"""

from decimal import Decimal
from datetime import datetime


class MySqlModel(dict):
    def __init__(self, **kwargs):
        super(MySqlModel, self).__init__(kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def to_display_dict(self):
        result = dict()
        for k, v in self.items():
            if isinstance(v, datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(v, Decimal):
                v = str(v)
            result.update({k: v})
        return result

def test():
    model = MySqlModel()
    model['name'] = 'test'
    model.age = 32
    print(model)

def main():
    test()

if __name__ == '__main__':
    main()
