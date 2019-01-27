# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move_type import MoveTypePayload


class TestMovesTypeEdit(BaseTestCase):
    """Test Moves Types edit"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_moves_types_edit_objects_are_immuable(self, username):
        user = getattr(self, username) if username else None
        MoveTypePayload().patch(1, user=user, code=405)
