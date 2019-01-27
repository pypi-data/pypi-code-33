# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.geokret_type import GeokretTypePayload


class TestGeokretyTypesCollection(BaseTestCase):
    """Test GeoKrety Types collection"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_geokrety_types_collection_has_right_number_of_items(self, username):
        user = getattr(self, username) if username else None
        GeokretTypePayload()\
            .get_collection(user=user)\
            .assertCount(5)
