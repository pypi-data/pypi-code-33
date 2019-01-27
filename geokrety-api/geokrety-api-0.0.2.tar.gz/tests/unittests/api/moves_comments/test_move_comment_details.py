# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move_comment import MoveCommentPayload


class TestMoveCommentDetails(BaseTestCase):
    """Test move comment details"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_as_(self, username):
        user = getattr(self, username) if username else None
        move_comment = self.blend_move_comment()
        MoveCommentPayload().get(move_comment.id, user=user)

    @request_context
    def test_has_public_attributes(self):
        move_comment = self.blend_move_comment()
        MoveCommentPayload()\
            .get(move_comment.id)\
            .assertHasPublicAttributes(move_comment)
