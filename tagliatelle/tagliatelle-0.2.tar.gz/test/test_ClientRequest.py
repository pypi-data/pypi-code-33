import unittest
try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

from mock import patch
from tagliatelle.ClientRequest import ClientRequest

from tagliatelle.data.TagBulkResponse import TagBulkResponse
from tagliatelle.data.TagResponse import TagResponse


class TestClientRequest(unittest.TestCase):

    def setUp(self):
        self.patcher_get_tags = patch('tagliatelle.LowLevelClient.LowLevelClient.get_tags')
        self.patcher_delete_tag = patch('tagliatelle.LowLevelClient.LowLevelClient.delete_tag')
        self.patcher_post_tag = patch('tagliatelle.LowLevelClient.LowLevelClient.post_tag')
        self.patcher_put_tag = patch('tagliatelle.LowLevelClient.LowLevelClient.put_tag')

        self.get_tags = self.patcher_get_tags.start()
        self.delete_tag = self.patcher_delete_tag.start()
        self.post_tag = self.patcher_post_tag.start()
        self.put_tag = self.patcher_put_tag.start()

    def tearDown(self):
        self.patcher_get_tags.stop()
        self.patcher_delete_tag.stop()
        self.patcher_post_tag.stop()
        self.patcher_put_tag.stop()

    def test_get_with_key(self):
        client_request = ClientRequest("", "http://test.url")
        client_request.with_key("urn:space").fetch()
        self.get_tags.assert_called_once_with("urn:space", None)

    def test_get_with_resource(self):
        client_request = ClientRequest("", "http://test.url")
        client_request.with_resource("http://test.resource.being.tagged").fetch()
        self.get_tags.assert_called_once_with(None, "http://test.resource.being.tagged")

    def test_get_with_key_and_resource(self):
        client_request = ClientRequest("", "http://test.url")
        client_request.with_key("urn:space").with_resource("http://test.resource.being.tagged").fetch()
        self.get_tags.assert_called_once_with("urn:space", "http://test.resource.being.tagged")

    def test_delete_with_resource(self):
        client_request = ClientRequest("", "http://test.url")
        tags = [TagResponse("urn:space", "value", "http://test.resource.being.tagged",
                            "52e90509-259f-460c-bc6b-4283941ea7ef", "", "", "", "", {}),
                TagResponse("urn:space", "value2", "http://test.resource.being.tagged",
                            "183529ce-9289-4d59-9e9b-f6196a6f0bac", "", "", "", "", {})]
        self.get_tags.return_value = TagBulkResponse(2, 2, 0, tags)
        client_request.with_key("urn:space").with_resource("http://test.resource.being.tagged").remove()
        self.assertEqual(1, self.get_tags.call_count)
        self.assertEqual(2, self.delete_tag.call_count)
        self.delete_tag.assert_any_call("183529ce-9289-4d59-9e9b-f6196a6f0bac")
        self.delete_tag.assert_any_call("52e90509-259f-460c-bc6b-4283941ea7ef")

    def test_update_tag(self):
        client_request = ClientRequest("", "http://test.url")
        tags = [TagResponse("urn:space", "value", "http://test.resource.being.tagged",
                            "52e90509-259f-460c-bc6b-4283941ea7ef", "", "", "", "", {})]
        self.get_tags.return_value = TagBulkResponse(1, 1, 0, tags)

        def side_effect(request):
            raise HTTPError("", 409, "CONFLICT", None, None)

        self.post_tag.side_effect = side_effect

        client_request.with_key("urn:space").with_resource("http://test.resource.being.tagged")\
            .with_string_value("test value").apply()
        self.assertEqual(1, self.get_tags.call_count)
        self.assertEqual(1, self.post_tag.call_count)
        self.assertEqual(1, self.put_tag.call_count)

        def Any(cls):
            class Any(cls):
                def __eq__(self, other):
                    return True

            return Any()

        self.put_tag.assert_any_call("52e90509-259f-460c-bc6b-4283941ea7ef", Any(object))


if __name__ == '__main__':
    unittest.main()
