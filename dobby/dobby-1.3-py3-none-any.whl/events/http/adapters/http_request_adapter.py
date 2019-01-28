from dobby.events.base.adapters.base_request_adapter import BaseRequestAdapter
from dobby.events.http.requests.http_request import HTTPRequest


class HTTPRequestAdapter(BaseRequestAdapter):

    def __init__(self):
        BaseRequestAdapter.__init__(self)

    def translate(self, event, context):
        return HTTPRequest(event, context)
