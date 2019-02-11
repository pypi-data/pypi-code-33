import os

import requests
from expiringdict import ExpiringDict
from rest_framework.utils import json
from django.conf import settings

try:
    from urllib.request import Request, urlopen  # Python 3
except ImportError:
    from urllib2 import Request, urlopen  # Python 2


class JSQLConnector:
    def checkIfObjectIsArray(self, object):
        return isinstance(object, list)

    def parseRequestToJSON(self, object):
        body_unicode = object.body.decode('utf-8')
        return json.loads(body_unicode)

    def parseStringToJSON(self, object):
        return json.loads(object)

    def retrieveDialect(self):
        headers = {'Content-Type': 'application/json', 'ApiKey': getattr(settings, "API_KEY", None),
                   'MemberKey': getattr(settings, "MEMBER_KEY", None)}
        resp = ""
        cache = ExpiringDict(max_len=100, max_age_seconds=10)
        cache["request"] = requests.get('http://localhost:9191/api/request/options/all', headers=headers)
        resp = cache.get("request").json()
        return {'code': resp["code"], 'data': resp}

    def getSQLQuery(self, token):
        headers = {'Content-Type': 'application/json', 'ApiKey': getattr(settings, "API_KEY", None),
                   'MemberKey': getattr(settings, "MEMBER_KEY", None)}
        resp = ""
        code = 100
        url = "http://localhost:9191/api/request/queries"
        if self.checkIfObjectIsArray(token):
            data = "[\""
            for t in token:
                data += t + "\", \""
            data = data[:-3] + "]"
            url += "/grouped"
        else:
            data = "[\"" + token + "\"]"
        r = requests.post(url, data=data, headers=headers)
        try:
            r.raise_for_status()
        except Exception:
            resp = json.loads(r.text)["message"]
        else:
            if self.checkIfObjectIsArray(r.json()):
                resp = r.json()[0]["query"]
                code = r.status_code
            else:
                resp = r.json()["description"]
                code = r.json()["code"]

        return {'code': code, 'data': resp}
