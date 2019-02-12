###################################################

import certifi
import urllib3

import json

from traceback import print_exc as pe

###################################################

http = urllib3.PoolManager(
    cert_reqs = 'CERT_REQUIRED',
    ca_certs = certifi.where()
)

###################################################

def geturl(url, headers = {}, encoding = "utf-8"):        
    try:
        print("getting", url)
        r = http.request("GET", url, headers = headers)
        content = r.data.decode(encoding)
        print("received length", len(content), "for", url)
    except:
        pe()
        content = None
    return content

def geturljson(url, headers = {}):            
    try:
        content = geturl(url, headers)
        obj = json.loads(content)        
    except:
        pe()
        obj = None
    return obj

###################################################
