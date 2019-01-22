#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-8-6 15:40:03
# @Author  : datachain

import http.client
import urllib
import json
import hashlib
import ssl
from qbase.common import configer as cf

ssl._create_default_https_context = ssl._create_unverified_context

def buildMySign(params,secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) +'&'
    data = sign+'secret_key='+secretKey
    return  hashlib.md5(data.encode("utf8")).hexdigest().upper()

def httpGet(url,resource,params=''):
    port = int(cf.configer().getValueByKey('proxy', 'port'))
    if port != 0:
        conn = http.client.HTTPSConnection('127.0.0.1', port=port, timeout=10)
        conn.set_tunnel(url)
    else:
        conn = http.client.HTTPSConnection(url, timeout=10)
    print(resource + '?' + params)
    conn.request("GET",resource + '?' + params)
    response = conn.getresponse()
    data = response.read().decode('utf-8')
    return json.loads(data)

def httpPost(url,resource,params):
     headers = {
            "Content-type" : "application/x-www-form-urlencoded",
     }
     port = int(cf.configer().getValueByKey('proxy', 'port'))
     if port != 0:
         conn = http.client.HTTPSConnection('127.0.0.1', port=port, timeout=10)
         conn.set_tunnel(url)
     else:
         conn = http.client.HTTPSConnection(url, timeout=10)
     temp_params = urllib.parse.urlencode(params)
     conn.request("POST", resource, temp_params, headers)
     response = conn.getresponse()
     data = response.read().decode('utf-8')
     params.clear()
     conn.close()
     return data


        
     
