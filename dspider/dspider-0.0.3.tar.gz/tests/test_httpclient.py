# Third Party Library
import pytest

# Dsipder Module
from dspider.request import HTTPMethod, Request


@pytest.mark.parametrize("method", [HTTPMethod.GET, HTTPMethod.POST])
@pytest.mark.parametrize("status", [200, 300, 400, 500])
@pytest.mark.asyncio
async def test_send_request(client, method, httpbin_url, status):
    url = httpbin_url / "status" / str(status)
    req = Request(url=url, method=method)
    resp = await client.send_request(req)
    assert resp.status == status


@pytest.mark.parametrize("method", [HTTPMethod.GET, HTTPMethod.POST])
@pytest.mark.parametrize("status", [200, 300, 400, 500])
@pytest.mark.asyncio
async def test_request_consume(
    queue_request, queue_response, method, httpbin_url, status
):
    url = httpbin_url / "status" / str(status)
    req = Request(url=url, method=method)
    await queue_request.put(req)
    resp, _req = await queue_response.get()
    assert _req is req
    assert resp.status == status
