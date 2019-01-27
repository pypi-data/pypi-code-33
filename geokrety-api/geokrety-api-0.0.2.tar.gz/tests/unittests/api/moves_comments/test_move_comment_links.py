# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move_comment import MoveCommentPayload


class TestMoveCommentLinks(BaseTestCase):
    """Test move comment links"""

    @request_context
    def test_move_comment_list_via_author(self):
        move_comment = self.blend_move_comment()
        response = MoveCommentPayload(_url_collection="/v1/users/{}/moves-comments".format(move_comment.author.id))\
            .get_collection()\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(move_comment)

    @request_context
    def test_move_comment_list_via_move(self):
        move_comment = self.blend_move_comment()
        response = MoveCommentPayload(_url_collection="/v1/moves/{}/moves-comments".format(move_comment.move.id))\
            .get_collection()\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(move_comment)
