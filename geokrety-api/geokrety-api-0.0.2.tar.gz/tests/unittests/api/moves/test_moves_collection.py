# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_move_type,
                                                  request_context)
from tests.unittests.utils.payload.move import MovePayload


class TestMoveCollection(BaseTestCase):
    """Test Move details"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],  # Owner
        ['user_2'],
    ])
    @request_context
    def test_move_collection_has_normal_attributes_as(self, username):
        user = getattr(self, username) if username else None
        moves = self.blend_move(author=self.user_1, count=3)
        response = MovePayload().get_collection(user=user)
        i = 0
        for response_ in response.data:
            response_.assertHasPublicAttributes(moves[i])
            i = i + 1

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_collection_has_coordinates(self, move_type):
        moves = self.blend_move(type=move_type, author=self.user_1, count=3)
        response = MovePayload().get_collection()
        i = 0
        for response_ in response.data:
            response_.assertHasPublicAttributes(moves[i])
            response_.assertHasAttribute('latitude', moves[i].latitude)
            response_.assertHasAttribute('longitude', moves[i].longitude)
            i = i + 1

    @parameterized.expand([
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_ARCHIVED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_collection_dont_have_coordinates_as(self, move_type):
        moves = self.blend_move(type=move_type, author=self.user_1, count=3)
        response = MovePayload().get_collection()
        i = 0
        for response_ in response.data:
            response_.assertHasPublicAttributes(moves[i])
            response_.assertHasAttribute('latitude', None)
            response_.assertHasAttribute('longitude', None)
            i = i + 1
