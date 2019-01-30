import os

import holvirc
import pytest
from holviapi.tests.fixtures import categoriesapi, invoicesapi, productsapi


@pytest.fixture
def connection():
    pool = os.environ.get('HOLVI_POOL', None)
    username = os.environ.get('HOLVI_USER', None)
    password = os.environ.get('HOLVI_PASSWORD', None)
    driverpath = os.environ.get('HOLVI_WEBDRIVER', 'holvirc.chromedriver.driver')
    if not pool or not username or not password:
        raise RuntimeError("HOLVI_POOL, HOLVI_USER and HOLVI_PASSWORD must be in ENV for these tests")
    cnc = holvirc.Connection.singleton(pool, username, password, driverpath)
    return cnc
