# -*- coding: utf-8 -*-

from parameterized import parameterized

from base_test_coordinates import _BaseTestCoordinates
from tests.unittests.utils.base_test_case import request_context
from tests.unittests.utils.payload.move import MovePayload


class _BaseTestCoordinatesOptional(_BaseTestCoordinates):
    """Base tests with optional coordinates"""

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
            .post(user=user)

    @request_context
    def test_field_altitude_default_value(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .post(user=self.user_1)\
            .assertHasAttribute('altitude', -32768)

    @request_context
    def test_field_country_default_value(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .post(user=self.user_1)\
            .assertHasAttribute('country', '')

    @request_context
    def test_field_distance_default_value(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .post(user=self.user_1)\
            .assertHasAttribute('distance', 0)

    @request_context
    def test_field_waypoint_default_value(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .post(user=self.user_1)\
            .assertHasAttribute('waypoint', '')

    @request_context
    def test_field_latitude_default_value(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .post(user=self.user_1)\
            .assertHasAttribute('latitude', None)

    @request_context
    def test_field_longitude_default_value(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .post(user=self.user_1)\
            .assertHasAttribute('longitude', None)

    @parameterized.expand([
        [0.0, None, 422, 'longitude'],
        [None, 0.0, 422, 'latitude'],
    ])
    @request_context
    def test_field_latitude_longitude_must_be_provided_at_the_same_time(self, latitude, longitude, expected, field=None):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates(latitude, longitude)\
            .post(user=self.user_1, code=expected)\
            .assertRaiseJsonApiError('/data/attributes/{}'.format(field))

    @request_context
    def test_field_latitude_longitude_may_be_both_none(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates(None, None)\
            .post(user=self.user_1)\
            .assertHasAttribute('latitude', None)\
            .assertHasAttribute('longitude', None)
