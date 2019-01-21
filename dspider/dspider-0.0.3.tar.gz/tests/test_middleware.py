# Third Party Library
import pytest

# Dsipder Module
from dspider.engine import Engine
from dspider.middleware import Middleware
from dspider.request import Request
from dspider.response import Response
from dspider.spider import Spider


@pytest.fixture
@pytest.mark.asyncio
async def engine(
    queue_class,
    httpclient_class,
    context_class,
    spider_manager_class,
    middleware_manager_class,
    event_loop,
):
    e = Engine(
        queue_class,
        httpclient_class,
        context_class,
        spider_manager_class,
        middleware_manager_class,
        loop=event_loop,
    )
    yield e
    await e.teardown()


@pytest.mark.asyncio
async def test_simple_middleware(engine, httpbin_url):
    class Retry500Middleware(Middleware):
        name = "retry500"

        async def handle_response(self, resp_or_exc, request):
            if not isinstance(resp_or_exc, Exception) and resp_or_exc.status == 500:
                if request.meta.get("retry", 0) < 3:
                    request.meta["retry"] = request.meta.get("retry", 0) + 1
                    await self.send_request(request)
                    return None
            return resp_or_exc, request

    count = 0

    class TestSpider(Spider):
        name = "test"

        async def start_requests(self):
            yield Request(url=httpbin_url / "status" / "500")

        async def handle_response(self, response, request):
            nonlocal count
            assert response is not None
            assert response.status == 500
            assert request.meta["retry"] == 3
            count += 1

    await engine.add_middleware(Retry500Middleware())
    await engine.setup()
    await engine.add_spider(TestSpider())
    await engine.join()
    assert count == 1


@pytest.mark.asyncio
async def test_send_request(engine, httpbin_url):
    class DupfilterMiddleware(Middleware):
        name = "Dupfilter"

        def __init__(self, *args, **kwargs):
            self.request_fingerprints = set()

            return super().__init__(*args, **kwargs)

        async def handle_request(self, request):
            request_fingerprint = request.url
            if request_fingerprint in self.request_fingerprints:
                return None

            self.request_fingerprints.add(request_fingerprint)
            return request

    count = 0

    class DupSpider(Spider):
        name = "dup"

        async def start_requests(self):
            yield Request(url=httpbin_url)
            yield Request(url=httpbin_url)

        async def handle_response(self, response, request):
            nonlocal count
            assert response is not None
            assert response.status == 200
            count += 1

    await engine.add_middleware(DupfilterMiddleware())
    await engine.setup()
    await engine.add_spider(DupSpider())
    await engine.join()
    assert count == 1


@pytest.mark.asyncio
async def test_send_response(engine, httpbin_url):
    class SendResponseMiddleware(Middleware):
        name = "send_resposne"

        def __init__(self, *args, **kwargs):
            self.request_fingerprints = set()

            return super().__init__(*args, **kwargs)

        async def setup(self, *args, **kwargs):
            await super().setup(*args, **kwargs)
            await self.send_response(
                Response(
                    url="",
                    status=200,
                    body=b"",
                    encoding="utf-8",
                    headers={},
                    cookies={},
                    meta={},
                    request=None,
                    history=[],
                ),
                Request(httpbin_url, meta={"spider": "test"}),
            )

    count = 0

    class TestSpider(Spider):
        name = "test"

        async def handle_response(self, response, request):
            nonlocal count
            assert response is not None
            assert response.status == 200
            count += 1

    await engine.add_middleware(SendResponseMiddleware())
    await engine.setup()
    await engine.add_spider(TestSpider())
    await engine.join()
    assert count == 1
