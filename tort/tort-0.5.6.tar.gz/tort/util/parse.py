from tornado.escape import json_decode
from tornado.web import HTTPError
from http import HTTPStatus

from .xml_etree import parse, ParseError


def parse_xml(response):
    if response.code == 599 or response.buffer is None:
        raise HTTPError(HTTPStatus.SERVICE_UNAVAILABLE, 'Response timeout or no body buffer')
    try:
        return parse(response.buffer)
    except ParseError:
        raise HTTPError(HTTPStatus.SERVICE_UNAVAILABLE, 'Unable to parse xml')


def parse_json(response):
    if response.code == 599 or response.body is None:
        raise HTTPError(HTTPStatus.SERVICE_UNAVAILABLE, 'Response timeout or no body')
    try:
        result = json_decode(response.body)
    except ValueError:
        raise HTTPError(HTTPStatus.SERVICE_UNAVAILABLE, 'Unable to parse json')
    return result
