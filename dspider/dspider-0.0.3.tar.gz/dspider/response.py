# Standard Library
from typing import Any, Dict, List, Optional

# Third Party Library
from yarl import URL

# Local Folder
from .request import Request
from .typedefs import Cookies, Headers


__all__ = ("Response",)


class Response:
    def __init__(
        self,
        url: URL,
        status: int,
        body: bytes,
        encoding: str,
        headers: Headers,
        cookies: Cookies,
        history: List[Request],
        meta: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ):
        self.url = url
        self.status = status
        self.body = body
        self.encoding = encoding
        self.headers = headers
        self.cookies = cookies
        self.history = history
        self.meta = meta or dict()

        self.request = request

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}(status={self.status})"

    @property
    def text(self) -> str:
        if not hasattr(self, "_text"):
            self._text = self.body.decode(self.encoding)

        return self._text
