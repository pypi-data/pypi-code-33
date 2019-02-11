from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
from unittest.mock import patch
from nose.tools import assert_list_equal

import simplejson as json
import requests

from searchlight_api.client import AccountService, SearchlightService


class MockServerRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(requests.codes.ok)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        if "/v3/locations?apiKey" in self.path:
            response_content = json.dumps([{
                    "locationId": "1",
                    "description": "United States"
                }]
            )
        elif "/v3/rank-sources?apiKey" in self.path:
            response_content = json.dumps([{
                    "baseDomain": "google.com",
                    "description": "Google (US / English)",
                    "rankSourceId": "1",
                    "name": "GOOGLE_EN_US"
                }]
            )
        elif "/v3/devices?apiKey" in self.path:
            response_content = json.dumps([{
                    "locationId": "1",
                    "description": "Desktop",
                    "deviceId": "1",
                }]
            )
        elif "/v3/accounts?apiKey" in self.path:
            response_content = json.dumps([{
                    "isActive": True,
                    "accountId": "10550",
                    "webProperties": "https://api.conductor.com/v3/"
                                     "accounts/10550/web-properties",
                    "name": "PS Reporting Test",
                }]
            )
        elif "/web-properties?apiKey" in self.path:
            response_content = json.dumps([{
                    "isActive": True,
                    "rankSourceInfo": [],
                    "webPropertyId": "43162",
                    "trackedSearchList": "https://api.conductor.com/v3/"
                                         "accounts/10550/web-properties/43162/"
                                         "tracked-searches",
                    "name": "conductor.com"
                }]
            )
        elif "/tracked-searches?apiKey" in self.path:
            response_content = json.dumps([{
                    "isActive": True,
                    "trackedSearchId": "7188291",
                    "preferredUrl": "http://www.conductor.com/",
                    "queryPhrase": "conductor",
                    "locationId": "1",
                    "rankSourceId": "1",
                    "deviceId": "1"
                }]
            )
        elif "/categories?apiKey" in self.path:
            response_content = json.dumps([{
                    "created": "2018-02-12T13:53:46.000Z",
                    "trackedSearchIds": [],
                    "modified": "2018-02-12T13:53:46.000Z",
                    "name": "Intent - Early - Why"
                }]
            )
        elif "/serp-items?apiKey" in self.path:
            response_content = json.dumps([{
                    "ranks": {
                        "UNIVERSAL_RANK": None,
                        "TRUE_RANK": 6,
                        "CLASSIC_RANK": 3
                    },
                    "webPropertyId": 43162,
                    "trackedSearchId": 7188291,
                    "itemType": "ANSWER_BOX",
                    "target": "",
                    "targetDomainName": "conductor.com",
                    "targetUrl": "https://www.conductor.com/blog"
                }]
            )
        elif "/search-volumes?apiKey" in self.path:
            response_content = json.dumps([{
                    "averageVolume": 135000,
                    "trackedSearchId": 7188291,
                    "volumeItems": []
                }]
            )
        else:
            response_content = None
        self.wfile.write(response_content.encode("utf-8"))
        return


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    address, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port):
    mock_server = HTTPServer(("localhost", port), MockServerRequestHandler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()


class TestMockServer(object):
    @classmethod
    def setup_class(cls):
        cls.mock_server_port = get_free_port()
        cls.mock_url = "http://localhost:{port}".format(
            port=cls.mock_server_port
        )
        start_mock_server(cls.mock_server_port)

    def test_get_locations(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            ss = SearchlightService()
            locations = ss.get_locations()
        assert_list_equal(locations, [{
            "locationId": "1",
            "description": "United States"}
        ])

    def test_get_rank_sources(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            ss = SearchlightService()
            rank_sources = ss.get_rank_sources()
        assert_list_equal(rank_sources, [{
                    "baseDomain": "google.com",
                    "description": "Google (US / English)",
                    "rankSourceId": "1",
                    "name": "GOOGLE_EN_US"
        }])

    def test_get_devices(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            ss = SearchlightService()
            devices = ss.get_devices()
        assert_list_equal(devices, [{
            "locationId": "1",
            "description": "Desktop",
            "deviceId": "1",
        }])

    def test_get_accounts(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            ss = SearchlightService()
            accounts = ss.get_accounts()
        assert_list_equal(accounts, [{
            "isActive": True,
            "accountId": "10550",
            "webProperties": "https://api.conductor.com/v3/"
                             "accounts/10550/web-properties",
            "name": "PS Reporting Test",
        }])

    def test_get_web_properties(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            account_service = AccountService(10550)
            web_properties = account_service.get_web_properties()
        assert_list_equal(web_properties, [{
            "isActive": True,
            "rankSourceInfo": [],
            "webPropertyId": "43162",
            "trackedSearchList": "https://api.conductor.com/v3/accounts/"
                                 "10550/web-properties/43162/tracked-searches",
            "name": "conductor.com"
        }])

    def test_get_tracked_searches(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            ss = AccountService(10550)
            tracked_searches = ss.get_tracked_searches(43162)
        assert_list_equal(tracked_searches, [{
            "isActive": True,
            "trackedSearchId": "7188291",
            "preferredUrl": "http://www.conductor.com/",
            "queryPhrase": "conductor",
            "locationId": "1",
            "rankSourceId": "1",
            "deviceId": "1"
        }])

    def test_get_categories(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            ss = AccountService(10550)
            categories = ss.get_categories()
        assert_list_equal(categories, [{
            "created": "2018-02-12T13:53:46.000Z",
            "trackedSearchIds": [],
            "modified": "2018-02-12T13:53:46.000Z",
            "name": "Intent - Early - Why"
        }])

    def test_get_ranks(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            ss = AccountService(10550)
            ranks = ss.get_ranks(43162, 1, "CURRENT")
        assert_list_equal(ranks, [{
             "ranks": {"UNIVERSAL_RANK": None, "TRUE_RANK": 6, "CLASSIC_RANK": 3},
             "webPropertyId": 43162,
             "trackedSearchId": 7188291,
             "itemType": "ANSWER_BOX",
             "target": "",
             "targetDomainName": "conductor.com",
             "targetUrl": "https://www.conductor.com/blog"
        }])

    def test_get_volume(self):
        with patch.dict("searchlight_api.client.__dict__", {"API_BASE_URL": self.mock_url}):
            ss = AccountService(10550)
            volume = ss.get_volume(43162, 1, "CURRENT")
        assert_list_equal(volume, [{
            "averageVolume": 135000,
            "trackedSearchId": 7188291,
            "volumeItems": []
        }])
