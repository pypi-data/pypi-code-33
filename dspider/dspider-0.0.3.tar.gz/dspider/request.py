# Standard Library
import enum
import json

from types import MethodType
from typing import Any, AnyStr, Dict, Optional, Union

# Third Party Library
from aiohttp import hdrs
from aiohttp.formdata import FormData
from aiohttp.multipart import MultipartWriter
from aiohttp.payload import BytesPayload
from multidict import CIMultiDict
from yarl import URL

# Dsipder Module
from dspider.typedefs import Cookies, Headers


__all__ = ("FormData", "HTTPMethod", "Request")


class HTTPMethod(enum.Enum):
    GET = "GET"
    POST = "POST"


class Request:
    """
    Request
    """

    def __init__(
        self,
        url: URL,
        method: HTTPMethod = HTTPMethod.GET,
        callback: Optional[Union[str, MethodType]] = None,
        body: AnyStr = None,
        data: Optional[Union[FormData, Dict[str, Any]]] = None,
        encoding: str = "utf-8",
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.url = url
        self.method = method
        if isinstance(callback, MethodType):
            callback = callback.__name__

        self.callback: Optional[str] = callback
        self.encoding = encoding
        if headers:
            self.headers = CIMultiDict(headers)
        else:
            self.headers = CIMultiDict()

        self.cookies = cookies or {}
        self.meta = meta or dict()

        self.body = None
        if body is not None:
            assert (
                self.method is HTTPMethod.POST
            ), "Can't send the body by using GET method"
            assert data is None, "Can't both set data and body"
            if isinstance(body, str):
                self.body = body.encode(self.encoding)
            else:
                self.body = body

        if data is not None:
            assert (
                self.method is HTTPMethod.POST
            ), "Can't send the body by using GET method"
            if isinstance(data, FormData):
                gen = data()
                if isinstance(gen, BytesPayload):
                    self.body = gen._value
                elif isinstance(gen, MultipartWriter):
                    assert False

                self.headers.update(gen.headers)
                assert gen.encoding is None or gen.encoding == self.encoding

            else:
                self.headers[hdrs.CONTENT_TYPE] = "application/json"
                self.body = json.dumps(data).encode(self.encoding)

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}(url={str(self.url)!r},method={self.method!s})"
