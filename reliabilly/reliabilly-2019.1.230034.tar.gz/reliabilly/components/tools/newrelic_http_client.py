import json
from reliabilly.settings import Settings
from reliabilly.components.web.http_requestor import HttpRequestor


class NewRelicHttpClient:
    def __init__(self, api_key, url=Settings.DATA_MONITORING_URL):
        self.api_key = api_key
        self.url = url

    def generate_headers(self):
        return {'Content-Type': 'application/json', 'X-Insert-Key': self.api_key}

    def create_event(self, payload, requestor=HttpRequestor()):
        headers = self.generate_headers()
        url = self.url
        proxy = {'http': Settings.PROXY_URL}
        response = requestor.post(url, data=json.dumps(payload), headers=headers, proxies=proxy)
        if response.status_code == 202:
            return True
        return False
