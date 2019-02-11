from unittest import TestCase, main
from unittest.mock import patch

from searchlight_api.client import AccountService


class BasicAnalysisTest(TestCase):

    @patch("searchlight_api.analysis.search_volume")
    def test_search_volume(self, mock_search_volume):
        mock_search_volume.return_value = [{
            "rankSourceId": 1,
            "trackedSearchId": 7188291,
            "averageVolume": 1000,
            "volumeItems": [],
            "webPropertyId": 100
        }]
        account_service = AccountService(10550)
        data = mock_search_volume(account_service, date="CURRENT")
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.analysis.rank_data")
    def test_rank_data(self, mock_rank_data):
        mock_rank_data.return_value = [{
            "targetWebPropertyId": 43162,
            "webPropertyId": 43162,
            "target": "",
            "targetDomainName": "conductor.com",
            "trueRank": 1,
            "classicRank": 1,
            "targetUrl": "https://www.conductor.com",
            "itemType": "STANDARD_LINK",
        }]
        account_service = AccountService(10550)
        data = mock_rank_data(account_service, date="CURRENT")
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)

    @patch("searchlight_api.analysis.all_tracked_searches")
    def test_all_tracked_searches(self, mock_all_tracked_searches):
        mock_all_tracked_searches.return_value = [{
            "deviceId": "1",
            "isActive": True,
            "locationId": "1",
            "preferredUrl": "http://www.conductor.com/",
            "queryPhrase": "conductor",
            "rankSourceId": "1",
            "trackedSearchId": 7188291,
            "webPropertyId": "43162"
        }]
        account_service = AccountService(10550)
        data = mock_all_tracked_searches(account_service)
        self.assertIsNotNone(data)
        self.assertIsInstance(data[0], dict)


if __name__ == "__main__":
    main()
