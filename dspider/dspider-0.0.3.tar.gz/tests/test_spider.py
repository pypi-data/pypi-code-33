# Standard Library
import asyncio

# Third Party Library
import pytest

# Dsipder Module
from dspider.request import Request
from dspider.response import Response
from dspider.spider import Spider


@pytest.mark.asyncio
async def test_run_dummy_spider(engine):
    class TestSpider(Spider):
        pass

    s = TestSpider()
    await engine.add_spider(s)
    await engine.join()


@pytest.mark.asyncio
async def test_run_spider(engine, httpbin_url):
    count = 0

    class TestSpider(Spider):
        name = "test"

        async def start_requests(self):
            yield Request(url=httpbin_url)
            yield Request(url=httpbin_url)

        async def handle_response(self, response: Response, request: Request):
            nonlocal count
            assert response is not None
            assert response.status == 200
            count += 1

    s = TestSpider()
    await engine.add_spider(s)
    await engine.join()
    assert count == 2


@pytest.mark.asyncio
async def test_custom_callback(engine, httpbin_url):
    count = 0

    class TestSpider(Spider):
        name = "test"

        async def start_requests(self):
            yield Request(url=httpbin_url, callback=self.handle_response_a)
            yield Request(url=httpbin_url, callback=self.handle_response_a)

        async def handle_response_a(self, response: Response, request: Request):
            nonlocal count
            assert response is not None
            assert response.status == 200
            count += 1

    s = TestSpider()
    await engine.add_spider(s)
    await engine.join()
    assert count == 2


@pytest.mark.asyncio
async def test_generate_new_request(engine, httpbin_url):
    count = 0

    class TestSpider(Spider):
        name = "test"

        async def start_requests(self):
            yield Request(url=httpbin_url)

        async def handle_response(self, response: Response, request: Request):
            nonlocal count
            assert response is not None
            assert response.status == 200
            count += 1
            if count < 2:
                yield Request(url=httpbin_url)

    s = TestSpider()
    await engine.add_spider(s)
    await engine.join()
    assert count == 2


@pytest.mark.asyncio
async def test_return_requests(engine, httpbin_url):
    count = 0

    class TestSpider(Spider):
        name = "test"

        async def start_requests(self):
            return [Request(url=httpbin_url)]

        async def handle_response(self, response: Response, request: Request):
            nonlocal count
            assert response is not None
            assert response.status == 200
            count += 1
            if count < 2:
                return Request(url=httpbin_url)

    s = TestSpider()
    await engine.add_spider(s)
    await engine.join()
    assert count == 2


@pytest.mark.asyncio
async def test_join_spider(engine):
    class TestSpider(Spider):
        def __init__(self, waiter):
            self.waiter = waiter

        async def start_requests(self):
            await self.waiter

    waiter_1 = asyncio.Future()
    s1 = TestSpider(waiter_1)
    s1.name = "test_1"
    waiter_2 = asyncio.Future()
    s2 = TestSpider(waiter_2)
    s2.name = "test_2"
    await engine.add_spider(s1)
    await engine.add_spider(s2)
    fut1 = asyncio.ensure_future(engine.join(s1))
    fut2 = asyncio.ensure_future(engine.join())

    await asyncio.sleep(0.3)
    assert not fut1.done()
    assert not fut2.done()

    waiter_1.set_result(None)
    await asyncio.sleep(0.3)
    assert fut1.done()
    assert not fut2.done()

    waiter_2.set_result(None)
    await asyncio.sleep(0.3)
    assert fut2.done()


@pytest.mark.asyncio
async def test_join_multi_times(engine):
    class TestSpider(Spider):
        def __init__(self, waiter):
            self.waiter = waiter

        async def start_requests(self):
            await self.waiter

    waiter = asyncio.Future()
    s = TestSpider(waiter)
    await engine.add_spider(s)
    fut1 = asyncio.ensure_future(engine.join(s))
    fut2 = asyncio.ensure_future(engine.join(s))
    fut3 = asyncio.ensure_future(engine.join())
    fut4 = asyncio.ensure_future(engine.join())
    futs = [fut1, fut2, fut3, fut4]
    await asyncio.sleep(0.3)
    for fut in futs:
        assert not fut.done()

    waiter.set_result(None)
    await asyncio.sleep(0.3)
    for fut in futs:
        assert fut.done()


@pytest.mark.asyncio
async def test_run_spider_when_no_setup(engine):
    class TestSpider(Spider):
        pass

    await engine.teardown()

    with pytest.raises(RuntimeError):
        await engine.add_spider(TestSpider())


@pytest.mark.asyncio
async def test_run_same_spider(engine):
    class TestSpider(Spider):
        pass

    await engine.add_spider(TestSpider())

    with pytest.raises(RuntimeError):
        await engine.add_spider(TestSpider())

    await engine.join()
