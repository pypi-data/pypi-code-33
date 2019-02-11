from unittest import TestCase, main
from unittest.mock import patch


class BasicSearchlightServiceUnitTest(TestCase):

    @patch("searchlight_api.client.SearchlightService")
    def test_get_locations(self, MockSearchlightService):
        ss = MockSearchlightService()
        ss.get_locations.return_value = [{
            "locationId": "1",
            "description": "United States"
        }]
        data = ss.get_locations()
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.client.SearchlightService")
    def test_get_rank_sources(self, MockSearchlightService):
        ss = MockSearchlightService()
        ss.get_rank_sources.return_value = [{
            "baseDomain": "google.com",
            "description": "Google (US / English)",
            "rankSourceId": "1",
            "name": "GOOGLE_EN_US"
        }]
        data = ss.get_rank_sources()
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.client.SearchlightService")
    def test_get_devices(self, MockSearchlightService):
        ss = MockSearchlightService()
        ss.get_devices.return_value = [{
            "locationId": "1",
            "description": "Desktop",
            "deviceId": "1",
        }]
        data = ss.get_devices()
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.client.SearchlightService")
    def test_get_accounts(self, MockSearchlightService):
        ss = MockSearchlightService()
        ss.get_accounts.return_value = [{
            "isActive": True,
            "accountId": "10550",
            "webProperties": "https://api.conductor.com/v3/accounts/"
                             "10550/web-properties",
            "name": "PS Reporting Test",
        }]
        data = ss.get_accounts()
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)


class BasicAccountServiceUnitTest(TestCase):

    @patch("searchlight_api.client.AccountService")
    def test_get_web_properties(self, MockAccountService):
        ss = MockAccountService(10550)
        ss.get_web_properties.return_value = [{
            "isActive": True,
            "rankSourceInfo": [],
            "webPropertyId": "43162",
            "trackedSearchList": "https://api.conductor.com/v3/accounts/10550/"
                                 "web-properties/43162/tracked-searches",
            "name": "conductor.com"
        }]
        data = ss.get_web_properties()
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.client.AccountService")
    def test_get_domain_name(self, MockAccountService):
        ss = MockAccountService(10550)
        ss.get_domain_name.return_value = "conductor.com"
        domain_name = ss.get_domain_name(43162)
        self.assertIsNotNone(domain_name)
        self.assertIsInstance(domain_name, str)

    @patch("searchlight_api.client.AccountService")
    def test_get_web_properties_for_domain(self, MockAccountService):
        ss = MockAccountService(10550)
        ss.et_web_properties_for_domain.return_value = [43162]
        wps = ss.et_web_properties_for_domain()
        self.assertIsNotNone(wps)
        self.assertIsInstance(wps[0], int)

    @patch("searchlight_api.client.AccountService")
    def test_get_tracked_searches(self, MockAccountService):
        ss = MockAccountService(10550)
        ss.get_tracked_searches.return_value = [{
            "isActive": True,
            "trackedSearchId": "7188291",
            "preferredUrl": "http://www.conductor.com/",
            "queryPhrase": "conductor",
            "locationId": "1",
            "rankSourceId": "1",
            "deviceId": "1"
        }]
        data = ss.get_tracked_searches(43162)
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.client.AccountService")
    def test_get_categories(self, MockAccountService):
        ss = MockAccountService(10550)
        ss.get_categories.return_value = [{
            "created": "2018-02-12T13:53:46.000Z",
            "trackedSearchIds": [],
            "modified": "2018-02-12T13:53:46.000Z",
            "name": "Intent - Early - Why"
        }]
        data = ss.get_categories()
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.client.AccountService")
    def test_get_ranks(self, MockAccountService):
        ss = MockAccountService(10550)
        ss.get_ranks.return_value = [{
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
        data = ss.get_ranks(43162, 1, "CURRENT")
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.client.AccountService")
    def test_get_volume(self, MockAccountService):
        ss = MockAccountService(10550)
        ss.get_volume.return_value = [{
            "averageVolume": 135000,
            "trackedSearchId": 7188291,
            "volumeItems": []
        }]
        data = ss.get_volume(43162, 1, "CURRENT")
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)


if __name__ == "__main___":
    main()
