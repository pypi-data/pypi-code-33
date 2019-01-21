# Standard Library
import json

# Third Party Library
import pytest

# Dsipder Module
from dspider.request import FormData, HTTPMethod, Request


def test_json_request(httpbin_url):
    req = Request(url=httpbin_url, method=HTTPMethod.POST, data={"type": "json"})
    assert req.body == b'{"type": "json"}'


def test_formdata_request(httpbin_url):
    req = Request(
        url=httpbin_url, method=HTTPMethod.POST, data=FormData([("type", "formdata")])
    )
    assert req.body == b"type=formdata"


@pytest.mark.asyncio
async def test_post_json_request(httpbin_url, client):
    data = {"type": "json"}
    req = Request(url=httpbin_url / "anything", method=HTTPMethod.POST, data=data)
    resp = await client.send_request(req)
    assert resp.status == 200
    resp_data = json.loads(resp.text)
    assert resp_data["json"] == data


@pytest.mark.asyncio
async def test_post_formdata_request(httpbin_url, client):
    data = FormData([("type", "formdata")])
    req = Request(url=httpbin_url / "anything", method=HTTPMethod.POST, data=data)
    resp = await client.send_request(req)
    assert resp.status == 200
    resp_data = json.loads(resp.text)
    assert resp_data["form"]["type"] == "formdata"
