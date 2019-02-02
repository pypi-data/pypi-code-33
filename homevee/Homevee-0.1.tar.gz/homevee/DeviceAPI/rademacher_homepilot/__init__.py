#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib

from homevee.Manager.gateway import get_gateway
from homevee.gateway_keys import RADEMACHER_HOMEPILOT

import heating_control
import blinds_control

def get_devices(db):
    data = get_gateway(RADEMACHER_HOMEPILOT, db)
    ip = data['IP']

    devices = []

    url = "http://"+ip+"/deviceajax.do?devices=1"

    response = urllib.urlopen(url).read()

    data = json.loads(response)

    for device in data['devices']:
        item = {'title': device['name'], 'id': device['did'], 'info': device['description']}

        devices.append(item)

    return {'devices': devices}