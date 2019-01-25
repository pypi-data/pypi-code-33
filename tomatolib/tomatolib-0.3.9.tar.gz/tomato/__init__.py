#!/usr/bin/python
# -*- coding:utf-8 -*-


import json
import ujson
import logging

logging.basicConfig(level=logging.INFO)

def patch_json():
    json.__name__ = 'ujson'
    json.dumps = ujson.dumps
    json.loads = ujson.loads
