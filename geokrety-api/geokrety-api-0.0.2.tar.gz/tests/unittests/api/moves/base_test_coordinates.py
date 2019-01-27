# -*- coding: utf-8 -*-

from parameterized import parameterized

from base_test_move_create import _BaseTestMoveCreate
from tests.unittests.utils.base_test_case import request_context
from tests.unittests.utils.payload.move import MovePayload
from tests.unittests.utils.static_test_cases import (BLANK_CHARACTERS_TEST_CASES,
                                                     FLOAT_TESTS_CASES)


class _BaseTestCoordinates(_BaseTestMoveCreate):
    """Base tests with optional coordinates"""

    @parameterized.expand([
        ['user_1'],
        ['user_2'],
        ['admin'],
    ])
    @request_context
    def test_field_waypoint_can_be_absent(self, username):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret()

        MovePayload(self.move_type, geokret)\
            .set_coordinates()\
            ._del_attribute('waypoint')\
            .post(user=user)\
            .assertHasAttribute('waypoint', '')

    @parameterized.expand([
        [None],
        [u''],
    ])
    @request_context
    def test_field_waypoint_can_be_empty(self, waypoint):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret)\
            .set_coordinates()\
            .set_waypoint(waypoint)\
            .post(user=self.user_1)\
            .assertHasAttribute('waypoint', '')

    @parameterized.expand([
        [u'ééééé'],
        [u'<'],
        [u'\x01 '],
        [u'";!'],
    ])
    @request_context
    def test_field_waypoint_must_be_alphanumeric(self, waypoint):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret)\
            .set_coordinates()\
            .set_waypoint(waypoint)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/waypoint')

    @parameterized.expand(BLANK_CHARACTERS_TEST_CASES)
    @request_context
    def test_field_waypoint_dont_accept_blank_characters(self, waypoint):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret)\
            .set_coordinates()\
            .set_waypoint(waypoint)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/waypoint')

    @parameterized.expand(FLOAT_TESTS_CASES)
    @request_context
    def test_field_latitude_must_be_decimal(self, latitude, expected):
        geokret = self.blend_geokret()
        payload = MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates(latitude, 0.0)
        if expected == 201:
            payload.post(user=self.user_1, code=expected)\
                .assertHasAttribute('latitude', float(latitude))
        else:
            payload.post(user=self.user_1, code=expected)\
                .assertRaiseJsonApiError('/data/attributes/latitude')

    @parameterized.expand(FLOAT_TESTS_CASES)
    @request_context
    def test_field_longitude_must_be_decimal(self, longitude, expected):
        geokret = self.blend_geokret()
        payload = MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates(0.0, longitude)
        if expected == 201:
            payload.post(user=self.user_1, code=expected)\
                .assertHasAttribute('longitude', float(longitude))
        else:
            payload.post(user=self.user_1, code=expected)\
                .assertRaiseJsonApiError('/data/attributes/longitude')

    @parameterized.expand([
        [-180.0],
        [-91.0],
        [-90.1],
        [-90.001],
        [90.001],
        [90.1],
        [91.0],
        [180.0],
    ])
    @request_context
    def test_field_latitude_must_be_valid(self, latitude):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates(latitude, 0.0)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/latitude')

    @parameterized.expand([
        [-250.0],
        [-181.0],
        [-180.1],
        [-180.001],
        [180.001],
        [180.1],
        [181.0],
        [250.0],
    ])
    @request_context
    def test_field_longitude_must_be_valid(self, longitude):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates(0.0, longitude)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/longitude')

    @request_context
    def test_altitude_is_computed_and_not_overridable(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            ._set_attribute('altitude', 666)\
            .post(user=self.user_1)\
            .assertHasAttribute('altitude', 996)

    @request_context
    def test_country_is_computed_and_not_overridable(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            ._set_attribute('country', 'pl')\
            .post(user=self.user_1)\
            .assertHasAttribute('country', 'FR')

    @request_context
    def test_distance_is_computed_and_not_overridable(self):
        geokret = self.blend_geokret()
        MovePayload(self.move_type, geokret=geokret)\
            .set_coordinates()\
            ._set_attribute('distance', 666)\
            .post(user=self.user_1)\
            .assertHasAttribute('distance', 0)
