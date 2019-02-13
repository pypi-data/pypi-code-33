import json
from tagliatelle import TAGLIATELLE_URL
from tagliatelle.data.TagBulkResponse import TagBulkResponse
from tagliatelle.data.TagResponse import TagResponse

try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError


class LowLevelClient:
    """This class wraps all the low level operations with Tagliatelle API"""

    def __init__(self, access_token, service_url):
        self.accessToken = access_token
        if service_url is None:
            self.serviceUrl = TAGLIATELLE_URL
        else:
            self.serviceUrl = service_url

    def get_tags(self, key="", resource_uri=""):
        try:
            query_params = {}

            if resource_uri is not None:
                query_params['resourceUri'] = resource_uri

            if key is not None:
                query_params['key'] = key

            req = Request(self.serviceUrl + "/v0/tags?" + urlencode(query_params))
            req.add_header('Authorization', 'Bearer ' + self.accessToken)

            response = urlopen(req)

            data = json.load(response)
            results = []
            if "results" in data:
                for tag in data["results"]:
                    results.append(TagResponse(tag.get("key"), tag.get("value"), tag.get("resourceUri"), tag.get("id"),
                                               tag.get("createdAt"), tag.get("createdBy"), tag.get("modifiedAt"),
                                               tag.get("modifiedBy"), tag.get("_links")))
                return TagBulkResponse(data.get('count'), data.get('total'), data.get('offset'), results)
            else:
                return TagBulkResponse(0, 0, 0, [])
        except HTTPError as e:
            print(e.read())

    def post_tag(self, request):
        try:
            req = Request(self.serviceUrl + "/v0/tags")
            req.add_header("Authorization", "Bearer " + self.accessToken)
            req.add_header("Content-Type", "application/json")
            req.get_method = lambda: 'POST'
            req.data = json.dumps(request)
            urlopen(req)
        except HTTPError as e:
            print(e.read())

    def put_tag(self, id, request):
        try:
            req = Request(self.serviceUrl + "/v0/tags/" + id)
            req.add_header("Authorization", "Bearer " + self.accessToken)
            req.add_header("Content-Type", "application/json")
            req.get_method = lambda: 'PUT'
            req.data = json.dumps(request)
            urlopen(req)
        except HTTPError as e:
            print(e.read())

    def delete_tag(self, id):
        try:
            req = Request(self.serviceUrl + "/v0/tags/" + id)
            req.add_header("Authorization", "Bearer " + self.accessToken)
            req.get_method = lambda: 'DELETE'
            urlopen(req)
        except HTTPError as e:
            print(e.read())



