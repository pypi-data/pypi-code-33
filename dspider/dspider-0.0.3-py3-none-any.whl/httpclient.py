# Standard Library
import asyncio

from typing import Callable, Optional

# Third Party Library
import aiohttp

# Local Folder
from .request import HTTPMethod, Request
from .response import Response
from .typedefs import (
    BaseFuture,
    FutureReturnResponse,
    Loop,
    RequestQueue,
    ResponseQueue,
)


__all__ = ("HTTPClient",)


class HTTPClient:
    def __init__(
        self,
        q_request: RequestQueue,
        q_response: ResponseQueue,
        *,
        loop: Optional[Loop] = None
    ):
        self.loop = loop or asyncio.get_event_loop()

        dummy = aiohttp.DummyCookieJar()
        self.session = aiohttp.ClientSession(loop=self.loop, cookie_jar=dummy)

        self.q_request = q_request
        self.q_reponse = q_response

        self._run_fut: Optional[BaseFuture] = None

    @property
    def running(self) -> bool:
        return self._run_fut is not None and not self._run_fut.done()

    async def setup(self) -> None:
        self._run_fut = asyncio.ensure_future(self.run())

    async def teardown(self) -> None:
        if self.running:
            assert self._run_fut is not None
            self._run_fut.cancel()
            await self._run_fut
            await self.session.close()

    async def send_request(self, req: Request) -> Response:
        if req.method == HTTPMethod.GET:
            coro = self.session.get(
                req.url, headers=req.headers, cookies=req.cookies, allow_redirects=False
            )
        elif req.method == HTTPMethod.POST:
            coro = self.session.post(
                req.url,
                headers=req.headers,
                cookies=req.cookies,
                data=req.body,
                allow_redirects=False,
            )
        else:
            raise ValueError("Unknown HTTPMethod %r" % (req.method,))

        async with coro as conn:
            body = await conn.read()
            resp = Response(
                url=conn.url,
                status=conn.status,
                body=body,
                encoding=conn.get_encoding(),
                headers=conn.headers,
                cookies=conn.cookies,
                history=conn.history,
                meta={},
                request=req,
            )
            return resp

    def make_response_collector(
        self, req: Request
    ) -> Callable[[FutureReturnResponse], None]:
        def response_collector(fut: FutureReturnResponse) -> None:
            resp_or_exc = fut.exception() or fut.result()
            self.q_reponse.put_nowait((resp_or_exc, req))

        return response_collector

    async def run(self) -> None:
        while self.running:
            try:
                req: Request = await self.q_request.get()
            except asyncio.CancelledError:
                return

            fut = asyncio.ensure_future(self.send_request(req), loop=self.loop)
            fut.add_done_callback(self.make_response_collector(req))
