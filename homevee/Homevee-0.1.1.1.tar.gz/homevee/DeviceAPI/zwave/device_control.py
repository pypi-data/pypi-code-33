#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os

import requests

from homevee.DeviceAPI.zwave.utils import do_zwave_request
from homevee.Manager.gateway import get_gateway


def get_data(device_id, db):
    return do_zwave_request("/ZAutomation/api/v1/devices/"+device_id, db)

def set_binary_device(device_id, value, db):
    return do_zwave_request("/ZAutomation/api/v1/devices/"+device_id+"/command/"+value, db)

def set_multistate_device(device_id, value, db):
    return do_zwave_request("/ZAutomation/api/v1/devices/"+device_id+"/command/exact?level="+value, db)