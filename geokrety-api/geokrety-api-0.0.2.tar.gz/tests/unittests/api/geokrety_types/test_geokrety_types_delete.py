# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.geokret_type import GeokretTypePayload


class TestGeokretyTypeDelete(BaseTestCase):
    """Test GeoKrety Types delete"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_geokrety_types_objects_are_immuable(self, username):
        user = getattr(self, username) if username else None
        GeokretTypePayload().delete(1, user=user, code=405)
