#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json


def readJson(path):
    file = open(path, "rb")
    fileJson = json.load(file)
    product_code = fileJson["product_code"]
    device_code = fileJson["device_code"]
    secret = fileJson["secret"]
    return {'product_code': product_code, 'device_code': device_code, 'secret': secret}
