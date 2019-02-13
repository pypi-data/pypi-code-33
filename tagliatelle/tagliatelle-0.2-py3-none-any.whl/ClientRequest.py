import json
from tagliatelle import TAGLIATELLE_URL
from tagliatelle.LowLevelClient import LowLevelClient
from tagliatelle.data.TagRequest import TagRequest

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

class ClientRequest:
    """This class wraps the high level operations that operate tags in Tagliatelle"""

    def __init__(self, access_token, url_override):
        self.tagRequest = TagRequest()
        self.accessToken = access_token
        if url_override is None:
            self.lowLevelClient = LowLevelClient(access_token, TAGLIATELLE_URL)
        else:
            self.lowLevelClient = LowLevelClient(access_token, url_override)

    def with_resource(self, resource_uri):
        self.tagRequest.resourceUri = resource_uri
        return self

    def with_key(self, key):
        self.tagRequest.key = key
        return self

    def with_string_value(self, string):
        self.tagRequest.value = string
        return self

    def with_object_value(self, obj):
        self.tagRequest.value = json.dumps(obj)
        return self

    def apply(self):
        self.__handle_operation_tag()

    def remove(self):
        self.__handle_operation_untag()

    def fetch(self):
        return self.__handle_operation_fetch()

    def __handle_operation_fetch(self):
        return self.lowLevelClient.get_tags(self.tagRequest.key, self.tagRequest.resourceUri)

    def __handle_operation_untag(self):
        bulk_tag_response = self.lowLevelClient.get_tags(self.tagRequest.key, self.tagRequest.resourceUri)
        for tag in bulk_tag_response.results:
            self.lowLevelClient.delete_tag(tag.id)

    def __handle_operation_tag(self):
        try:
            self.lowLevelClient.post_tag(self.tagRequest)
        except HTTPError as e:
            if e.code == 409:
                bulk_response = self.lowLevelClient.get_tags(self.tagRequest.key, self.tagRequest.resourceUri)
                if bulk_response.total != 1:
                    raise Exception("Unable to update the tag")
                tag = bulk_response.results[0]
                self.lowLevelClient.put_tag(tag.id, self.tagRequest)

