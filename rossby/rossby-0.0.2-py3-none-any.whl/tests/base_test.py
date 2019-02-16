import unittest
from rossby import Rossby
import requests


class BaseTestClass(unittest.TestCase):
    rossby = Rossby()
    session = requests.Session()

    def plain_request(self, endpoint, params):
        resp = self.session.get(f"https://api.weather.gov/{endpoint}", params=params)

        return resp.json()

    def icon_request(self, endpoint, params):
        resp = self.session.get(f"https://api.weather.gov/{endpoint}", params=params)

        return resp
