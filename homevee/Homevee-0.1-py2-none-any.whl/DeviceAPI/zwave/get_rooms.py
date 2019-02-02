#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import requests

from homevee.Manager.gateway import get_gateway
from homevee.db_utils import get_database_con


def get_rooms():
    result = {}

    gateway_data = get_gateway('Z-Wave', get_database_con())

    port = ""
    if (gateway_data['PORT'] != None and gateway_data['PORT'] != ""):
        port = ":" + str(gateway_data['PORT'])



    url = "http://" + gateway_data['KEY1'] + ':' + gateway_data['KEY2'] + '@' + gateway_data['IP'] + port + "/ZAutomation/api/v1/locations/"
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    request = requests.get(url, headers=headers)
    data = request.content

    print data

    result = json.loads(data)

    return result