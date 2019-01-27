# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move import MovePayload


class TestMoveLinks(BaseTestCase):
    """Test Move links"""

    @request_context
    def test_user_details_via_move_comment(self):
        move_comment = self.blend_move_comment()
        payload = MovePayload(_url="/v1/moves-comments/{}/move")

        payload.get(move_comment.id)\
            .assertHasPublicAttributes(move_comment.move)
        payload.get(666, code=404)\
            .assertRaiseJsonApiError('move_comment_id')
