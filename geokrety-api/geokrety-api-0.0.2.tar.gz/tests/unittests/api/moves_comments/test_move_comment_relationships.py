# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move_comment import MoveCommentPayload


class TestMoveCommentRelationships(BaseTestCase):
    """Test move comment relationships"""

    @request_context
    def test_move_comment_author_relationship(self):
        move_comment = self.blend_move_comment(author=self.user_1)
        MoveCommentPayload(_url="/v1/moves-comments/{}/relationships/author")\
            .get(move_comment.id)\
            .assertHasData('user', self.user_1.id)

    @request_context
    def test_move_comment_move_relationship(self):
        move = self.blend_move()
        move_comment = self.blend_move_comment(move=move)
        MoveCommentPayload(_url="/v1/moves-comments/{}/relationships/move")\
            .get(move_comment.id)\
            .assertHasData('move', move.id)
