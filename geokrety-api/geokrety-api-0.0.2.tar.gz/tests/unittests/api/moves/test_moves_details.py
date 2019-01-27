# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_move_type,
                                                  request_context)
from tests.unittests.utils.payload.move import MovePayload


class TestMoveDetails(BaseTestCase):
    """Test Move details"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],  # Owner
        ['user_2'],
    ])
    @request_context
    def test_move_details_has_public_attributes_as(self, username):
        user = getattr(self, username) if username else None
        move = self.blend_move()
        MovePayload().get(move.id, user=user)\
            .assertHasPublicAttributes(move)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
        [MOVE_TYPE_GRABBED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_details_has_coordinates_as(self, move_type):
        move = self.blend_move(type=move_type)
        MovePayload().get(move.id)\
            .assertHasPublicAttributes(move)\
            .assertHasAttribute('latitude', move.latitude)\
            .assertHasAttribute('longitude', move.longitude)\
            .assertHasAttribute('altitude', move.altitude)\
            .assertHasAttribute('country', move.country)\
            .assertHasAttribute('distance', move.distance)

    @parameterized.expand([
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_ARCHIVED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_details_dont_have_coordinates_as(self, move_type):
        move = self.blend_move(type=move_type)
        MovePayload().get(move.id)\
            .assertHasPublicAttributes(move)\
            .assertAttributeNotPresent('latitude')\
            .assertAttributeNotPresent('longitude')\
            .assertAttributeNotPresent('altitude')\
            .assertAttributeNotPresent('country')\
            .assertAttributeNotPresent('distance')
