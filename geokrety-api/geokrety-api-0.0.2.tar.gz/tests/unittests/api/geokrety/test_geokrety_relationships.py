# -*- coding: utf-8 -*-

from app.api.helpers.data_layers import GEOKRET_TYPE_HUMAN
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.geokret import GeokretPayload


class TestGeokretyRelationships(BaseTestCase):
    """Test GeoKrety relationships"""

    @request_context
    def test_geokrety_owner_relationship(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload(_url="/v1/geokrety/{}/relationships/owner")\
            .get(geokret.id, user=self.user_2)\
            .assertHasData('user', self.user_1.id)

    @request_context
    def test_geokrety_holder_relationship(self):
        geokret = self.blend_geokret(holder=self.user_1)
        GeokretPayload(_url="/v1/geokrety/{}/relationships/holder")\
            .get(geokret.id, user=self.user_2)\
            .assertHasData('user', self.user_1.id)

    @request_context
    def test_geokrety_type_relationship(self):
        geokret = self.blend_geokret(type=GEOKRET_TYPE_HUMAN)
        GeokretPayload(_url="/v1/geokrety/{}/relationships/type")\
            .get(geokret.id, user=self.user_2)\
            .assertHasData('geokrety-type', GEOKRET_TYPE_HUMAN)
