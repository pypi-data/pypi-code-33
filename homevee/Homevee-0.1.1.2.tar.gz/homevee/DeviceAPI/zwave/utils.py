#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import requests
from homevee.Manager.gateway import get_gateway


def do_zwave_request(path, db):
    gateway_data = get_gateway("Z-Wave", db)
    port = ""
    if (gateway_data['PORT'] != None and gateway_data['PORT'] != ""):
        port = ":" + str(gateway_data['PORT'])

    url = "http://" + gateway_data['KEY1'] + ':' + gateway_data['KEY2'] + '@' + gateway_data[
        'IP'] + port + path

    #print url

    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    request = requests.get(url, headers=headers)
    data = request.content

    #print data

    json_data = json.loads(data)

    #print url, json_data

    return json_data