import os
import time

import pytest

from .fixtures import categoriesapi, connection
from .test_holviapi_idempotent import test_get_category

pytestmark = pytest.mark.skipif((not os.environ.get('HOLVI_POOL') or not os.environ.get('HOLVI_USER') or not os.environ.get('HOLVI_PASSWORD') or not bool(os.environ.get('HOLVI_ALLOW_SLOW'))), reason="HOLVI_POOL, HOLVI_USER, HOLVI_PASSWORD and HOLVI_ALLOW_SLOW must be in ENV for these tests")


def test_session_autoreinit_after_expiry(categoriesapi):
    # first run a test and get the current session id
    test_get_category(categoriesapi)
    old_sessionid = categoriesapi.connection.apiconnection.session.cookies['sessionid']

    # Sleep until session expires
    sleeptime = categoriesapi.connection.token_expires - time.time() + 2
    time.sleep(sleeptime)

    # run test again, get new sessionid
    test_get_category(categoriesapi)
    new_sessionid = categoriesapi.connection.apiconnection.session.cookies['sessionid']

    assert old_sessionid != new_sessionid
