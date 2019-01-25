import os
import requests

VMAAS_SERVER_DEFAULT = "https://webapp-vmaas-stable.1b13.insights.openshiftapps.com"


class VmaasApi:
    def __init__(self):
        self.server = os.getenv("VMAAS_SERVER", VMAAS_SERVER_DEFAULT)
        if self.server.endswith("/"):
            self.server = self.server[:-1]
    
    def _vmaas_call(self, method, endpoint, data=None):
        if method == "GET":
            result = requests.get("%s%s" % (self.server, endpoint))
        elif method == "POST":
            result = requests.post("%s%s" % (self.server, endpoint), data=data)
        else:
            raise ValueError("Unknown method: %s" % method)

        return result.text
    
    def get_version(self):
        return self._vmaas_call("GET", "/api/v1/version")

    def print_status(self):
        print("VMAAS_SERVER: %s" % self.server)
        print("Server version: %s" % self.get_version())
