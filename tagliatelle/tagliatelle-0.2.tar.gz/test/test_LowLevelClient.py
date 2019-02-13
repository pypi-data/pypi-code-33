import json
import unittest
from mock import patch
from MockResponse import MockResponse

from tagliatelle.LowLevelClient import LowLevelClient
from tagliatelle.data.TagRequest import TagRequest


class TestLowLevelClient(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('tagliatelle.LowLevelClient.urlopen')
        self.urlopen_mock = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_delete_tag(self):
        low_level_client = LowLevelClient("", "http://test.url")

        def side_effect(request):
            self.assertEqual("DELETE", request.get_method())
            self.assertEqual("http://test.url/v0/tags/020da5ca-c2bf-4ac4-beb4-5e19eda2a200", request.get_full_url())

        self.urlopen_mock.side_effect = side_effect
        low_level_client.delete_tag("020da5ca-c2bf-4ac4-beb4-5e19eda2a200")

    def test_put_tag(self):
        low_level_client = LowLevelClient("", "http://test.url")

        def side_effect(request):
            self.assertEqual("PUT", request.get_method())
            self.assertEqual("http://test.url/v0/tags/ed9caa8d-40e9-4dbe-869e-9e5b6b787e73", request.get_full_url())

            self.urlopen_mock.side_effect = side_effect
            request = TagRequest("urn:space", "saturn", "http://test.url")
            low_level_client.put_tag("ed9caa8d-40e9-4dbe-869e-9e5b6b787e73", "http://test.resource.being.tagged")

    def test_post_tag(self):
        low_level_client = LowLevelClient("", "http://test.url")

        def side_effect(request):
            self.assertEqual("POST", request.get_method())
            self.assertEqual("http://test.url/v0/tags", request.get_full_url())

        self.urlopen_mock.side_effect = side_effect
        low_level_client.post_tag("http://test.resource.being.tagged")

    def test_get_no_tags(self):
        low_level_client = LowLevelClient("", "http://test.url")
        self.urlopen_mock.return_value = MockResponse("{}")
        bulk_respose = low_level_client.get_tags("http://test.resource.being.tagged")
        self.assertEqual(0, bulk_respose.count)
        self.assertEqual(0, bulk_respose.total)
        self.assertEqual(0, bulk_respose.offset)
        self.assertEqual([], bulk_respose.results)

    def test_get_tags(self):
        low_level_client = LowLevelClient("", "http://test.url")
        obj = {
            "count": 2,
            "total": 2,
            "results": [
                {
                    "id": "c121efe0-bee6-4c84-be92-8907502c21c6",
                    "key": "urn:namespace:configuration",
                    "value": "sample value 1",
                    "resourceUri": "http://test.resource.being.tagged",
                    "createdAt": "2018-11-03T01:12:36.720Z",
                    "createdBy": "wa|b3d162c7-ffdb-4455-8068-1eae2e1f5e93",
                    "modifiedAt": "2019-02-10T21:38:43.346Z",
                    "modifiedBy": "waad|7Q4pxFe7EGs_VN5XuG1fMswSspASn6DpUecPJAIas8U",
                    "_links": {
                        "self": {
                            "href": "http://test.url/v0/tags/62528803-fa37-4bd7-b885-7be87abd15da"
                        }
                    }
                },
                {
                    "id": "c1edf452-c0e5-4f32-aa70-8950ff061ed3",
                    "key": "urn:namespace:configuration",
                    "value": "sample value 2",
                    "resourceUri": "http://test.resource.being.tagged",
                    "createdAt": "2018-11-21T08:54:23.390Z",
                    "createdBy": "wa|0873d114-c034-4a49-8ae7-2be9a315fc94",
                    "modifiedAt": "2019-02-08T15:58:04.935Z",
                    "modifiedBy": "waad|7Q4pxFe7EGs_VN5XuG1fMswSspASn6DpUecPJAIas8U",
                    "_links": {
                        "self": {
                            "href": "http://test.url/v0/tags/888bae24-5db3-4ab4-85dc-5d6ac6b718d5"
                        }
                    }
                }]
        }
        self.urlopen_mock.return_value = MockResponse(json.dumps(obj))
        bulk_respose = low_level_client.get_tags("http://test.resource.being.tagged")
        self.assertEqual(2, bulk_respose.count)
        self.assertEqual(2, bulk_respose.total)
        self.assertEqual("http://test.resource.being.tagged", bulk_respose.results[0].resourceUri)
        self.assertEqual("http://test.resource.being.tagged", bulk_respose.results[1].resourceUri)


if __name__ == '__main__':
    unittest.main()
