import os

import pytest
from holviapi.tests.test_api_dangerous import test_create_delete_invoice, test_create_send_invoice

from .fixtures import categoriesapi, connection, invoicesapi, productsapi

pytestmark = pytest.mark.skipif((not os.environ.get('HOLVI_POOL') or not os.environ.get('HOLVI_USER') or not os.environ.get('HOLVI_PASSWORD') or not bool(os.environ.get('HOLVI_ALLOW_DANGEROUS'))), reason="HOLVI_POOL, HOLVI_USER, HOLVI_PASSWORD and HOLVI_ALLOW_DANGEROUS must be in ENV for these tests")
