# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.geokret import GeokretPayload


class TestGeokretyDelete(BaseTestCase):
    """Test Geokrety delete"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 403],
        ['user_2', 403],
    ])
    @request_context
    def test_delete_as(self, username, expected):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret()
        GeokretPayload().delete(geokret.id, user=user, code=expected)
