import ujson

from nanohttp import context
from nanohttp.exceptions import HTTPKnownStatus


class HTTPTooManyRequests(HTTPKnownStatus):
    status = '429 Too Many Requests'

    def __init__(self, wait_time=0):
        self.wait_time = wait_time
        super().__init__(self.status)

    def render(self):
        context.response_encoding = 'utf-8'
        context.response_content_type = 'application/json'
        return ujson.encode(dict(
            wait=self.wait_time
        ))
