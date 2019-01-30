import os

import pytest
from holviapi.tests.test_api_idempotent import test_get_invoice, test_list_invoices

from .fixtures import categoriesapi, connection, invoicesapi, productsapi

pytestmark = pytest.mark.skipif((not os.environ.get('HOLVI_POOL') or not os.environ.get('HOLVI_USER') or not os.environ.get('HOLVI_PASSWORD')), reason="HOLVI_POOL, HOLVI_USER and HOLVI_PASSWORD must be in ENV for these tests")
