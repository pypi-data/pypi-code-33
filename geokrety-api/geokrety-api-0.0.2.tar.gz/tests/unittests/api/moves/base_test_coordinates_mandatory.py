# -*- coding: utf-8 -*-

from parameterized import parameterized

from base_test_coordinates import _BaseTestCoordinates
from tests.unittests.utils.base_test_case import request_context
from tests.unittests.utils.payload.move import MovePayload


class _BaseTestCoordinatesMandatory(_BaseTestCoordinates):
    """Base tests with mandatory coordinates"""

    @parameterized.expand([
        ['user_1'],
        ['user_2'],
        ['admin'],
    ])
    @request_context
    def test_as(self, username):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            .post(user=user)

    @parameterized.expand([
        ['user_1'],
        ['user_2'],
        ['admin'],
    ])
    @request_context
    def test_field_latitude_must_be_present(self, username):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_attribute('latitude')\
            .post(user=user, code=422)\
            .assertRaiseJsonApiError('/data/attributes/latitude')

    @parameterized.expand([
        ['user_1'],
        ['user_2'],
        ['admin'],
    ])
    @request_context
    def test_field_longitude_must_be_present(self, username):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_attribute('longitude')\
            .post(user=user, code=422)\
            .assertRaiseJsonApiError('/data/attributes/longitude')

    @parameterized.expand([
        [None],
        [u''],
    ])
    @request_context
    def test_field_latitude_cannot_be_empty(self, latitude):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            ._set_attribute('latitude', latitude)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/latitude')

    @parameterized.expand([
        [None],
        [u''],
    ])
    @request_context
    def test_field_longitude_cannot_be_empty(self, longitude):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            ._set_attribute('longitude', longitude)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/longitude')
