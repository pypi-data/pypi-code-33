#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `search_in_api` package."""

import pytest

from search_in_api import search_in_api


@pytest.fixture
def params():
    """
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return {
        "xml_url": "https://raw.githubusercontent.com/archatas/search_in_api/master/tests/data/sample-data.xml",
        "json_url": "https://raw.githubusercontent.com/archatas/search_in_api/master/tests/data/sample-data.json",
        "tag": "artist",
        "value": "Joachim Pastor",
    }


def test_search_in_xml_endpoint(params):
    """Test the core function"""
    pages = search_in_api.search_for_string(
        url=params['xml_url'],
        tag=params['tag'],
        value=params['value'],
    )
    assert pages == [
        "https://raw.githubusercontent.com/archatas/search_in_api/master/tests/data/sample-data.xml",
        "https://raw.githubusercontent.com/archatas/search_in_api/master/tests/data/sample-data3.xml",
    ]


def test_search_in_json_endpoint(params):
    """Test the core function"""
    pages = search_in_api.search_for_string(
        url=params['json_url'],
        tag=params['tag'],
        value=params['value'],
    )
    assert pages == [
        "https://raw.githubusercontent.com/archatas/search_in_api/master/tests/data/sample-data.json",
        "https://raw.githubusercontent.com/archatas/search_in_api/master/tests/data/sample-data3.json",
    ]
