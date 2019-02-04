import json
import random
import string
import warnings
from json import JSONDecodeError
from typing import Union, Callable, Optional, Tuple, Any, Dict, Collection, List
from urllib.parse import urlparse

from tornado.httpclient import HTTPResponse, HTTPRequest, AsyncHTTPClient
from tornado import httputil
from tornado.httputil import HTTPHeaders, HTTPServerRequest
from tornado.web import RequestHandler, HTTPError
from logging import getLogger, Logger

from http_server_base import BasicResponder
from http_server_base.tools import logging_method, ExtendedLogger, RequestLogger, SubrequestFailedErrorCodes, ConfigLoader
from http_server_base.tools import JsonSerializable
from http_server_base.tools import ServerError, SubrequestFailedError
from http_server_base.tools import HttpSubrequest, HttpSubrequestResponse

# noinspection PyAttributeOutsideInit
class Logged_RequestHandler(RequestHandler):
    """
    Logged_RequestHandler class
    This is a template to the handler classes.
    """
    
    # Must override
    logger_name:str
    
    # Should not override
    logger: ExtendedLogger = None
    request_id = None
    request: httputil.HTTPServerRequest
    _async_http_client: AsyncHTTPClient = None
    
    # Could override
    responder_class: BasicResponder
    request_id_possible_query_names: List[str] = [ 'requuid', 'requ_id', 'request-id', 'requestId', 'request_id' ]
    request_id_header_name: str = 'X-Request-Id'
    request_id_possible_header_names: List[str] = [ request_id_header_name, 'RequestId' ]
    
    _ARG_DEFAULT = object()
    def get_body_or_query_argument(self, name, default=_ARG_DEFAULT, strip=True):
        all_args = self.request.body_arguments.copy()
        all_args.update(self.request.query_arguments)
        return self._get_argument(name=name, default=default, source=all_args, strip=strip)
    
    def get_body_or_query_arguments(self, name, strip=True):
        all_args = self.request.body_arguments.copy()
        all_args.update(self.request.query_arguments)
        return self._get_arguments(name=name, source=all_args, strip=strip)
    
    @property
    def requ_id(self) -> str:
        warnings.warn("The 'requ_id' field is going to be deprecated, use 'request_id' instead.", DeprecationWarning, 2)
        return self.request_id
    
    @requ_id.setter
    def requ_id(self, value):
        warnings.warn("The 'requ_id' field is going to be deprecated, use 'request_id' instead.", DeprecationWarning, 2)
        self.request_id = value
    
    @property
    def async_http_client(self) -> AsyncHTTPClient:
        if (self._async_http_client is None):
            self._async_http_client = AsyncHTTPClient()
        
        return self._async_http_client
    
    #region Initialization
    def initialize(self, **kwargs):
        """
        Initializes the Logged_RequestHandler
        
        Initializes the logging.
        Logs the incoming request to the DEBUG level.
        Sets an request id.
        """
        if (getattr(self, 'logger_name', None) is None):
            self.logger_name = type(self).__name__
        
        super().initialize(**kwargs)
        
        _logger:ExtendedLogger = getLogger(self.logger_name)
        self.logger:ExtendedLogger = RequestLogger(self, _logger)
        
        request_obj = self.request
        self.request_id = self.generate_request_id(search_in_query=True, search_in_headers=True)
    
    def prepare(self):
        super().prepare()
        self.dump_request(self.request, request_name="Incoming", prefix='req', dump_body=ConfigLoader.get_from_config('HTTP/dumpRequestBody', default=False))
    #endregion
    #region Responders
    def set_default_headers(self):
        del self._headers["Content-Type"]
    
    def resp_error(self, code=500, reason=None, message=None, *args, **kwargs):
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            self.send_error(code, reason=reason)
            return
        
        responder.resp_error(self, code=code, reason=reason, message=message, *args, **kwargs)
    
    def resp(self, code=200, reason=None, message=None, *args, **kwargs):
        BasicResponder.resp_success(handler=self, code=code, reason=reason, message=message, *args, **kwargs)
    
    def resp_success(self, code=200, reason=None, message=None, result=None, *args, **kwargs):
        if (hasattr(self, 'responder_class')):
            responder = self.responder_class
        elif (hasattr(self.application, 'responder_class')):
            responder = self.application.responder_class
        else:
            self.set_status(code, reason=reason)
            return
        
        responder.resp_success(self, code=code, reason=reason, message=message, result=result, *args, **kwargs)
    #endregion
    #region Subrequests
    #region Fetching
    async def _fetch__form_request(self, request: Union[str, HTTPRequest], *, add_request_id: bool, **kwargs) -> HttpSubrequest:
        if (not isinstance(request, HttpSubrequest)):
            request = HttpSubrequest(url=request, request_id=self.generate_request_id(), parent_request_id=self.request_id, base_logger=self.logger, **kwargs)
        
        if (add_request_id):
            await self._fetch__form_request__add_request_id(request)
        
        return request
    async def _fetch__form_request__add_request_id(self, request: HttpSubrequest):
        if (not isinstance(request.headers, HTTPHeaders)):
            request.headers = HTTPHeaders(request.headers)
        request.headers.add(self.request_id_header_name, request.request_id)
    async def _fetch__fetch_request(self, request: HttpSubrequest) -> HttpSubrequestResponse:
        request.logger.debug(f"Request: {request.method} {request.url}")
        _client = self.async_http_client
        response = await _client.fetch(request, raise_error=False, callback=None)
        response = HttpSubrequestResponse(response)
        request.logger.debug(f"Response: {response.request.method} {response.request.url}; Code: {response.code}; Content-length: {len(response.body or '')}")
        self.dump_response(response, request_name=f"Subrequest {request.request_id}", logger=request.logger, prefix='resp')
        return response
    async def _fetch__check_response(self, response: HttpSubrequestResponse, *, expected_codes: Collection[int], expected_content_type: Optional[str]):
        response.request.logger.trace("Checking response...")
        alert = None
        
        if (alert is None and response.code not in expected_codes):
            alert = dict(expected_codes=expected_codes)
        
        if (alert is None and expected_content_type):
            if ('Content-Type' not in response.headers):
                alert = dict(message="Missing 'Content-Type' header in the response", expected_mime_type=expected_content_type)
            elif (expected_content_type not in { _h.partition(';')[0] for _h in response.headers.get_list('Content-Type') }):
                alert = dict(message=f"Missing '{expected_content_type}' in 'Content-Type' headers of the response ({','.join(response.headers.get_list('Content-Type'))})", expected_mime_type=expected_content_type)
        
        if (alert is not None):
            exception = SubrequestFailedError(response, **alert)
            response.request.logger.warning(str(exception))
            if (response.error and not isinstance(response.error, HTTPError)):
                response.request.logger.warning(f"Base error: {str(response.error)}")
            raise exception
    async def fetch(self, request: Union[str, HTTPRequest], *, raise_error: bool = True, expected_codes: Union[int, Collection[int]] = 200, expected_content_type: str = None, add_request_id: bool = True, **kwargs) -> HttpSubrequestResponse:
        """
        Fetches the specified request and asynchronously returns response.
        Minorly logs both request and response objects.
        Response is the instance of HttpSubrequestResponse (child of HTTPResponse).
        
        If the `raise_error` option is set, the request status code is checked to be one of `expected_codes` parameter.
        If the `raise_error` option is set, the mime type of response will be checked to have value of `expected_content_type` parameter.
        If the `add_request_id` option is set, the request object will have appropriate.
        All other parameters are nested from the original `tornado.httpclient.AsyncHTTPClient.fetch()`.
        
        :param request: str or HTTPRequest
        :param raise_error: bool
        :param expected_codes: int or Collection[int]
        :param expected_content_type: str or None
        :param add_request_id: bool
        
        :raises: SubrequestFailedError
        :returns: HttpSubrequestResponse
        """
        
        request = await self._fetch__form_request(request, add_request_id=add_request_id, **kwargs)
        response = await self._fetch__fetch_request(request)
        if (raise_error):
            if (expected_codes is None):
                expected_codes = [ 200 ]
            elif (isinstance(expected_codes, int)):
                expected_codes = [ expected_codes ]
            await self._fetch__check_response(response, expected_codes=expected_codes, expected_content_type=expected_content_type)
        
        return response
    async def fetch_json(self, request: Union[str, HTTPRequest], *, check_content_type_header: bool = True, json_load_options: Dict[str, Any] = None, **kwargs) -> Tuple[HttpSubrequestResponse, JsonSerializable]:
        """
        Fetches the specified request for the JSON data and asynchronously returns both response and loaded JSON object.
        Minorly logs both request and response objects.
        Response is the instance of HttpSubrequestResponse (child of HTTPResponse).
        
        The `raise_error` is always overridden to True.
        If the `check_content_type_header` option is set, the request headers will be checked to have 'Content-Type: application/json'.
        The `json_load_options` parameter is expanded to keyword-params of the json.loads() method.
        All other parameters are nested from the `fetch()` method above.
        
        :param request: str or HTTPRequest
        :param check_content_type_header: bool
        :param json_load_options: kwargs 
        
        :raises: SubrequestFailedError
        :returns: Tuple[HttpSubrequestResponse, JsonSerializable]
        """
        
        base_error: Optional[SubrequestFailedError] = None
        kwargs.pop('raise_error', None)
        try:
            response = await self.fetch(request, raise_error=True, expected_content_type='application/json' if (check_content_type_header) else None, **kwargs)
        except SubrequestFailedError as e:
            base_error = e
            response = base_error.response
        
        alert = None
        resp_data = None
        resp_json = None
        
        if (response.body is None):
            alert = dict(message="Server responded empty body while JSON was expected to be", error_code=SubrequestFailedErrorCodes.InvalidResponseBody)
        
        if (alert is None and (not base_error or base_error.error_code != SubrequestFailedErrorCodes.MimeTypeMismatch)):
            if (json_load_options is None):
                json_load_options = dict()
            
            try:
                resp_data = response.body.decode()
                resp_json: Dict[str, Any] = json.loads(resp_data, **json_load_options)
            except JSONDecodeError:
                alert = dict(message=f"Cannot decode JSON from the response: '{resp_data}'", server_response=str(resp_data), error_code=SubrequestFailedErrorCodes.InvalidResponseBody)
            except Exception as e:
                alert = dict(code=500, error="Unknown Error", message=f"Unknown error: {e}")
        
        if (alert is None and base_error):
            if (resp_json is not None):
                alert = dict(message=resp_json.get('reason') or resp_json.get('error') or resp_json.get('message'), server_response=resp_json, error_code=SubrequestFailedErrorCodes.InvalidResponseBody)
            else:
                alert = dict(server_response=response.body.decode())
        
        if (alert is not None):
            raise SubrequestFailedError(response, base_error=base_error, **alert)
        
        return response, resp_json
    async def fetch_binary_data(self, request: Union[str, HTTPRequest], **kwargs) -> Tuple[HttpSubrequestResponse, bytes]:
        """
        Fetches the specified request for the binary data and asynchronously returns both response and loaded bytes.
        Minorly logs both request and response objects.
        Response is the instance of HttpSubrequestResponse (child of HTTPResponse).
        
        The `raise_error` is always overridden to True.
        All other parameters are nested from the `fetch()` method above.
        
        :param request: str or HTTPRequest
        
        :raises: SubrequestFailedError
        :returns: Tuple[HttpSubrequestResponse, bytes]
        """
        
        base_error: Optional[SubrequestFailedError] = None
        kwargs.pop('raise_error', None)
        try:
            response = await self.fetch(request, raise_error=True, **kwargs)
        except SubrequestFailedError as e:
            base_error = e
            response = base_error.response
        
        alert = None
        resp_data = None
        
        if (response.body is None):
            alert = dict(message="Server responded empty body", error_code=SubrequestFailedErrorCodes.InvalidResponseBody)
        if (not alert and base_error):
            try:
                resp_data = response.body.decode()
                resp_json: Dict[str, Any] = json.loads(resp_data)
            except JSONDecodeError:
                alert = dict(code=503, message=f"Unexpected error code: {response.code}, response is not JSON: '{resp_data}'", server_response=str(resp_data))
            except Exception as e:
                alert = dict(code=500, error="Unknown Error", message=f"Unknown error: {e}")
            else:
                alert = dict(message=resp_json.get('reason') or resp_json.get('error') or resp_json.get('message'), server_response=resp_json)
        
        if (alert):
            raise SubrequestFailedError(response, base_error=base_error, **alert)
        
        return response, response.body
    #endregion
    #region Proxying
    def generate_proxy_request(self, handler):
        """
        Generate the new instance of the tornado.httpclient.HTTPRequest.
        :param handler:
        :return:
        """
        warnings.warn("The 'generate_proxy_request' method has redundant arguments, "
            "use 'generate_proxy_HTTPRequest' instead. It is going to be changed in v1.0", DeprecationWarning, 2)
        handler.generate_proxy_HTTPRequest()
    
    def generate_proxy_HTTPRequest(self, **kwargs) -> HTTPRequest:
        request_obj:httputil.HTTPServerRequest = self.request
        
        protocol = kwargs.pop('protocol', request_obj.protocol)
        server = kwargs.pop('host', kwargs.pop('server', request_obj.host))
        uri = kwargs.pop('uri', request_obj.uri)
        new_url = kwargs.pop('url', f"{protocol}://{server}{uri}")
        
        _headers = HTTPHeaders(kwargs.pop('headers', request_obj.headers))
        _headers['Connection'] = 'keep-alive'
        _headers.pop('Host', None)
        _method = kwargs.pop('method', request_obj.method).upper()
        _body = kwargs.pop('body', request_obj.body)
        _headers.pop('Transfer-Encoding', None)
        if (_body):
            _headers['Content-Length'] = len(_body)
        else:
            _headers.pop('Content-Length', None)
        _allow_nonstandard_methods = kwargs.pop('allow_nonstandard_methods', True)
        
        _proxy_request = HTTPRequest(url=new_url, method=_method, body=_body, headers=_headers, allow_nonstandard_methods=_allow_nonstandard_methods, **kwargs)
        return _proxy_request
    
    async def proxy_request_async_2(self, *, generate_request_func: Optional[Callable[[RequestHandler], HTTPRequest]]=None, **kwargs):
        """
        Proxies current request.
        """
        
        if (generate_request_func is None):
            generate_request_func = type(self).generate_proxy_HTTPRequest
        
        _client = AsyncHTTPClient()
        _proxy_request = generate_request_func(self, **kwargs)
        
        self.dump_request(_proxy_request, request_name='Proxy Request', prefix='proxy')
        self.logger.debug("Fetching proxy request", prefix='proxy')
        resp = await _client.fetch(_proxy_request, raise_error=False)
        self.__proxied(resp)
    
    def proxy_request_async(self, *, generate_request_func: Optional[Callable[['Logged_RequestHandler'], HTTPRequest]]=None, **kwargs):
        """
        Proxies current request.
        """
        
        if (generate_request_func is None):
            generate_request_func = type(self).generate_proxy_HTTPRequest
        
        _client = AsyncHTTPClient()
        _proxy_request = generate_request_func(self, **kwargs)
        
        self.dump_request(_proxy_request, request_name='Proxy Request', prefix='proxy')
        self.logger.debug("Fetching proxy request", prefix='proxy')
        _client.fetch(_proxy_request, callback=self.__proxied, raise_error=False)
        return
    
    def __proxied(self, response: HTTPResponse):
        _code = response.code
        self.logger.trace("Proxying response:\nHTTP/1.1 {0} {1}\n{2}\nBody: {3} bytes", response.code, response.reason, response.headers, len(response.body or ''))
        if (_code == 599):
            self.logger.error(f"{type(response.error).__name__}: {response.error}", prefix='resp')
            if (isinstance(response.error, (ConnectionRefusedError, TimeoutError))):
                _new_code = 503
                _host = urlparse(response.request.url).netloc
                _message = f"{response.error.strerror}: {_host}"
            else:
                _new_code = 500
                _message = f"Internal error during proxying the request: {response.error}"
            _reason = None
            self.logger.error(f"{_message}. Changing request code from {_code} to {_new_code}", prefix='resp')
            self.resp_error(_new_code, reason=_reason, message=_message)
            return
        
        self.logger.debug("Return {0}", _code, prefix='resp')
        self.set_status(_code)
        for _header_name, _header_value in response.headers.items(): # type: str, str
            if (not (_header_name.lower().startswith(('access-control-', 'transfer-') or _header_name.lower() in ('host', 'date', 'connection')))):
                self.set_header(_header_name, _header_value)
        self.set_header('Content-Length', len(response.body or ''))
        self.set_header('Connection', 'close')
        self.clear_header('Transfer-Encoding')
        if (response.body):
            self.logger.debug(f"Content {response.body[:500]}", prefix='resp')
            self.write(response.body)
        else:
            self.write(b'')
        self.finish()
        return
    #endregion
    #endregion
    
    #region Finisher overrides
    # Overriding original finish to exclude 204/304 no body verification
    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        if (self._finished):
            raise RuntimeError("finish() called twice")
        
        if (chunk is not None):
            self.write(chunk)
        
        # Automatically support ETags and add the Content-Length header if
        # we have not flushed any content yet.
        if (not self._headers_written):
            if (self._status_code == 200 and
                self.request.method in ("GET", "HEAD") and
                    "Etag" not in self._headers):
                self.set_etag_header()
                if (self.check_etag_header()):
                    self._write_buffer = []
                    self.set_status(304)
            # if (self._status_code in (204, 304)):
            #     assert not self._write_buffer, "Cannot send body with %s" % self._status_code
            #     self._clear_headers_for_304()
            content_length = sum(len(part) for part in self._write_buffer)
            self.set_header("Content-Length", content_length)
        
        if hasattr(self.request, "connection"):
            # Now that the request is finished, clear the callback we
            # set on the HTTPConnection (which would otherwise prevent the
            # garbage collection of the RequestHandler when there
            # are keepalive connections)
            self.request.connection.set_close_callback(None)
        
        self.flush(include_footers=True)
        self.request.connection.finish()
        self._log()
        self._finished = True
        self.on_finish()
        self._break_cycles()
    def write_error(self, *args, exc_info: Tuple = None, **kwargs):
        if (exc_info):
            exception_type, exception, traceback = exc_info
            if (issubclass(exception_type, ServerError)):
                self.resp_error(**exception.resp_error_params)
                return
        
        return super().write_error(*args, exc_info=exc_info, **kwargs)
    #endregion
    
    @classmethod
    def generate_random_string(cls, N):
        return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=N))
    def generate_request_id(self, *, search_in_query: bool = False, search_in_headers: bool = False) -> str:
        if (search_in_query):
            for _query_param_name in self.request_id_possible_query_names:
                _from_query = self.get_query_argument(_query_param_name, None)
                if (_from_query):
                    return _from_query
        
        if (search_in_headers):
            for _header_param_name in self.request_id_possible_header_names:
                _from_headers = self.request.headers.get(_header_param_name, None)
                if (_from_headers):
                    return _from_headers
        
        return "{0:x}".format(random.randint(0x10000000, 0xffffffff))
    
    #region Logging
    @classmethod
    def _str_or_bytes_to_str(cls, x: Union[str, bytes, None]) -> str:
        if (not x):
            return ''
        elif (isinstance(x, str)):
            return x
        elif (isinstance(x, bytes)):
            return x.decode()
        else:
            raise ValueError(f"Argument must be either str, bytes, or None, not {type(x)}")
    
    @logging_method
    def dump_request(self, request_obj: Union[HTTPServerRequest, HTTPRequest], *, request_name: str = '', logger: ExtendedLogger = None, dump_body: bool = False, **kwargs):
        if (logger is None):
            logger = self.logger
        
        _is_server_request = isinstance(request_obj, HTTPServerRequest)
        _url = request_obj.uri if _is_server_request else request_obj.url
        logger.info("{0} HTTP request: {1} {2}", request_name, request_obj.method, _url, **kwargs)
        logger.debug("{0} Headers: {1}", request_name, dict(request_obj.headers), **kwargs)
        if (_is_server_request):
            logger.debug("{0} Query args: {1}", request_name, request_obj.query_arguments, **kwargs)
            logger.debug("{0} Body args: {1}", request_name, request_obj.body_arguments, **kwargs)
        else:
            logger.debug("{0} Body: {1}", request_name, request_obj.body, **kwargs)
        
        logger.trace \
        (
            "{0} Dump:\n"
            "{1} {2} HTTP/1.1\n"
            "{3}\n" # This is the double linebreak, because headers do already have the trailing linebreak
            "Body: {4} bytes\n"
            "{5}",
            request_name,
            request_obj.method, _url,
            HTTPHeaders(request_obj.headers),
            len(request_obj.body or ''),
            dump_body and self._str_or_bytes_to_str(request_obj.body),
            **kwargs,
        )
    @logging_method
    def dump_response(self, response_obj: Union[HTTPResponse], *, request_name: str = '', logger: ExtendedLogger = None, dump_body: bool = False, **kwargs):
        if (logger is None):
            logger = self.logger
        
        _is_server_request = False
        request_obj: HTTPRequest = response_obj.request
        _url = request_obj.uri if _is_server_request else request_obj.url
        logger.info("{0} HTTP response: {1} {2}", request_name, response_obj.code, response_obj.reason, **kwargs)
        logger.debug("{0} Headers: {1}", request_name, dict(response_obj.headers), **kwargs)
        if (_is_server_request):
            logger.debug("{0} Query args: {1}", request_name, response_obj.query_arguments, **kwargs)
            logger.debug("{0} Body args: {1}", request_name, response_obj.body_arguments, **kwargs)
        else:
            logger.debug("{0} Body: {1}", request_name, response_obj.body, **kwargs)
        
        logger.trace \
        (
            "{0} Dump:\n"
            "HTTP/1.1 {1} {2}\n"
            "{3}\n" # This is the double linebreak, because headers do already have the trailing linebreak
            "Body: {4} bytes\n"
            "{5}",
            request_name,
            response_obj.code, response_obj.reason,
            HTTPHeaders(response_obj.headers),
            len(response_obj.body or ''),
            dump_body and self._str_or_bytes_to_str(response_obj.body),
            **kwargs,
        )
    def log_exception(self, typ, value, tb):
        pass
    #endregion
