# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

import pytest
from pyprimed.pio import Pio


@pytest.yield_fixture(scope="function")
def pio(monkeypatch):
    from pyprimed.api import Client

    def mock_auth(*args, **kwargs):
        pass

    monkeypatch.setattr(Client, "_auth", mock_auth)

    yield Pio(uri="http://user:user@localhost:5000")


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")
