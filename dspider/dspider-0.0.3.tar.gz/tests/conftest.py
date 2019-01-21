# Standard Library
import shlex
import socket
import sys
import time

from subprocess import Popen
from typing import AsyncGenerator, Generator, Type

# Third Party Library
import pytest

from yarl import URL

# Dsipder Module
from dspider.ctx import Context
from dspider.engine import Engine
from dspider.httpclient import HTTPClient
from dspider.middleware import MiddlewareManager
from dspider.queue import Queue
from dspider.spider import SpiderManager
from dspider.typedefs import BaseQueue, Loop


def unused_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    addr = s.getsockname()
    s.close()
    return addr[1]


@pytest.fixture(scope="session")
def _httpbin_port() -> int:
    return unused_port()


@pytest.fixture(scope="session")
def httpbin(_httpbin_port: int) -> Generator[None, None, None]:
    p = Popen(shlex.split(f"{sys.executable} -m httpbin.core --port {_httpbin_port}"))
    while p.poll() is None:
        try:
            socket.create_connection(("localhost", _httpbin_port)).close()
            break
        except ConnectionRefusedError:
            time.sleep(0.01)
    else:
        assert False, "httpbin process exit unexpectedly"
    yield
    p.terminate()


@pytest.fixture(scope="session")
def httpbin_port(httpbin: None, _httpbin_port: int) -> int:
    return _httpbin_port


@pytest.fixture(scope="session")
def httpbin_url(httpbin_port: int) -> URL:
    return URL(f"http://localhost:{httpbin_port}/")


@pytest.fixture
def queue_class() -> Type[BaseQueue]:
    return Queue


@pytest.fixture
def httpclient_class() -> Type[HTTPClient]:
    return HTTPClient


@pytest.fixture
def context_class() -> Type[Context]:
    return Context


@pytest.fixture
def spider_manager_class() -> Type[SpiderManager]:
    return SpiderManager


@pytest.fixture
def middleware_manager_class() -> Type[MiddlewareManager]:
    return MiddlewareManager


@pytest.fixture
@pytest.mark.asyncio
async def engine(
    queue_class: Type[BaseQueue],
    httpclient_class: Type[HTTPClient],
    context_class: Type[Context],
    spider_manager_class: Type[SpiderManager],
    middleware_manager_class: Type[MiddlewareManager],
    event_loop: Loop,
) -> AsyncGenerator[Engine, None]:
    e = Engine(
        queue_class,
        httpclient_class,
        context_class,
        spider_manager_class,
        middleware_manager_class,
        loop=event_loop,
    )
    await e.setup()
    yield e
    if e.running:
        await e.teardown()


@pytest.fixture
def _queue_request(event_loop: Loop, queue_class: Type[BaseQueue]) -> BaseQueue:
    return queue_class(loop=event_loop)


@pytest.fixture
def _queue_response(event_loop: Loop, queue_class: Type[BaseQueue]) -> BaseQueue:
    return queue_class(loop=event_loop)


@pytest.fixture
@pytest.mark.asyncio
async def client(
    event_loop: Loop, _queue_request: BaseQueue, _queue_response: BaseQueue
) -> AsyncGenerator[HTTPClient, None]:
    client = HTTPClient(_queue_request, _queue_response, loop=event_loop)
    await client.setup()
    yield client
    await client.teardown()


@pytest.fixture
def queue_request(client: HTTPClient, _queue_request: BaseQueue) -> BaseQueue:
    return _queue_request


@pytest.fixture
def queue_response(client: HTTPClient, _queue_response: BaseQueue) -> BaseQueue:
    return _queue_response
