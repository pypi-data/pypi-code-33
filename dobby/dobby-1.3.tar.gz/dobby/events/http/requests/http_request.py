from dobby.events.base.requests.base_request import BaseRequest
import json


class HTTPRequest(BaseRequest):
    """Http request class"""

    def __init__(self, event, context):
        print(event)
        if event['body']:
            body = json.loads(event['body'])
        else:
            body = {}
        BaseRequest.__init__(self, body)

        self._path_parameters = event['pathParameters']
        self._queryStringParameters = event['queryStringParameters']
        self._requestContext = context

    def getPathParameters(self):
        return self._path_parameters

    def getQueryStringParameters(self):
        return self._queryStringParameters

    def getRequestContext(self):
        return self._requestContext

