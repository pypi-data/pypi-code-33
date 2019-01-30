#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json


class PropMessage(object):
    def __init__(self, flag, value):
        self.id = None
        self.flag = flag
        self.value = value

    def __str__(self):
        return json.dumps({
            'id': self.id,
            'flag': self.flag,
            'value': self.value
        })

    __repr__ = __str__


if __name__ == '__main__':
    aa = PropMessage("flag", "asd")
    print aa
    print type(str({"flag": "flag", "value": "asd"}))
