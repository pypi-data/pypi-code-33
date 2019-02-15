import os
import asyncio
import time
from itertools import count
import hashlib
import random
from urllib.parse import urlunsplit, parse_qs, urlsplit
from collections import namedtuple

import tornado.web
import tornado.httpclient
from tornado.options import options, define

from .request_id import set as set_request_id
from .logger import PageLogger
from .util.request import HTTPTortRequest, make_qs, real_ip
from .util.parse import parse_json, parse_xml


define('tort_max_clients', default=200, type=int, help='Max clients (requests) for http_client')
define('tort_timeout_multiplier', default=1.0, type=float, help='Timeout multiplier (affects all requests)')

stats = count()


RequestResult = namedtuple('RequestResult', ['response', 'data'])


def _gen_requestid():
    return hashlib.md5('{}{}{}'.format(os.getpid(), next(stats), random.random()).encode('utf-8')).hexdigest()


class RequestHandler(tornado.web.RequestHandler):
    def initialize(self, *args, **kwargs):
        self.request_id = self.request.headers.get('X-Request-Id', _gen_requestid())
        set_request_id(self.request_id)

        self.log = PageLogger(self.request, self.request_id,
                              handler_name=(type(self).__module__ + '.' + type(self).__name__))

        self.http_client = self.initialize_http_client()

        self.responses = {}

    @staticmethod
    def get_global_http_client():
        if not hasattr(RequestHandler, '_http_client'):
            RequestHandler._http_client = tornado.httpclient.AsyncHTTPClient(
                max_clients=options.tort_max_clients)

        return RequestHandler._http_client

    def initialize_http_client(self):
        return self.get_global_http_client()

    def on_finish(self):
        self.log.complete_logging(self.get_status())

    def make_request(self, name, method='GET', full_url=None, url_prefix=None, path='', data='', headers=None,
                     connect_timeout=1, request_timeout=2, follow_redirects=True, retry_count=0, **kwargs):
        """
        Class for easier constructing ``tornado.httpclient.HTTPRequest`` object.
        Request url could be constructed with two ways:
            * ``full_url`` argument
            * ``url_prefix`` as domain part and ``path`` as path part
        :param string name: Name of the request (for later accessing response through ``self.responses.get(name)``)
        :param string method: HTTP method, e.g. "GET" or "POST"
        :param string full_url: Full url for the requesting server (ex. ``http://example.com``)
        :param string url_prefix: Request url domain part
        :param string path: Request url path part
        :param data: Query to be passed to the request (could be a dict and would be translated to a query string)
        :type data: `string` or `dict`
        :param headers: Additional HTTP headers to pass on the request
        :type headers: ``tornado.httputil.HTTPHeaders`` or `dict`
        :param float connect_timeout: Timeout for initial connection in seconds
        :param float request_timeout: Timeout for entire request in seconds
        :param bool follow_redirects: Should redirects be followed automatically or return the 3xx response?
        :param int retry_count: How much  times the request should retry
        :param kwargs: any other ``tornado.httpclient.HTTPRequest`` arguments
        :return: ``tornado.httpclient.HTTPRequest``
        """

        if (full_url is None) == (url_prefix is None):
            raise TypeError('make_request required path/url_prefix arguments pair or full_url argument')
        if full_url is not None and path != '':
            raise TypeError("Can't combine full_url and path arguments")

        scheme = 'http'
        query = ''
        body = None

        if full_url is not None:
            parsed_full_url = urlsplit(full_url)
            scheme = parsed_full_url.scheme
            url_prefix = parsed_full_url.netloc
            path = parsed_full_url.path
            query = parsed_full_url.query

        if method in ['GET', 'HEAD', 'DELETE']:
            parsed_query = parse_qs(query)
            parsed_query.update(data if isinstance(data, dict) else parse_qs(data))
            query = make_qs(parsed_query)
        else:
            body = make_qs(data) if isinstance(data, dict) else data

        headers = {} if headers is None else headers

        headers.update({
            'X-Forwarded-For': real_ip(self.request),
            'X-Request-Id': self.request_id,
            'Content-Type': headers.get('Content-Type', 'application/x-www-form-urlencoded')
        })

        request_params = dict(
            url=urlunsplit((scheme, url_prefix, path, query, '')),
            method=method,
            headers=headers,
            body=body,
            connect_timeout=connect_timeout * options.tort_timeout_multiplier,
            request_timeout=request_timeout * options.tort_timeout_multiplier,
            follow_redirects=follow_redirects,
            **kwargs
        )

        return HTTPTortRequest(name, retry_count, **request_params)

    def _process_response(self, response) -> RequestResult:
        content_type = response.headers.get('Content-Type', '').split(';')[0]

        data = None
        try:
            if 'xml' in content_type:
                data = parse_xml(response)
            elif content_type == 'application/json':
                data = parse_json(response)
        except:
            self.log.warning('Could not parse response with Content-Type header')

        return RequestResult(response, data)

    async def fetch_request(self, request):
        if isinstance(request, (tuple, list)):
            assert len(request) in (2, 3)
            request = self.make_request(name=request[0], method='GET', full_url=request[1],
                                        data=request[2] if len(request) == 3 else '')

        self.log.request_started(request)

        try:
            result = self._process_response(await self.http_client.fetch(request.request, raise_error=False))
        except Exception as e:
            result = RequestResult(tornado.httpclient.HTTPResponse(
                request.request,
                599,
                error=e,
                request_time=time.time() - request.request.start_time,
                start_time=request.request.start_time
            ), None)

        self.log.request_complete(result.response)

        if result.response.code >= 500 and request.retry_count > 0:
            result = await self.fetch_request(request.retry())

        self.responses[request.name] = result

        return result

    async def fetch_requests(self, requests):
        return await asyncio.gather(*[self.fetch_request(request) for request in requests])
