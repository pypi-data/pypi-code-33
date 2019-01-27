# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move_type import MoveTypePayload


class TestMovesTypeDelete(BaseTestCase):
    """Test Moves Types delete"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_moves_types_objects_are_immuable(self, username):
        user = getattr(self, username) if username else None
        MoveTypePayload().delete(1, user=user, code=405)
