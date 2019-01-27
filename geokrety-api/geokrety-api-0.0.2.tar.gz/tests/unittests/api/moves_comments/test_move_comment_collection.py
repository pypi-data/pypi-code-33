# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move_comment import MoveCommentPayload


class TestMoveCommentCollection(BaseTestCase):
    """Test move comment collection"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_has_public_attributes_as_(self, username):
        user = getattr(self, username) if username else None
        move_comments = self.blend_move_comment(count=3)
        response = MoveCommentPayload()\
            .get_collection(user=user)\
            .assertCount(3)
        response.data[0].assertHasPublicAttributes(move_comments[0])
        response.data[1].assertHasPublicAttributes(move_comments[1])
        response.data[2].assertHasPublicAttributes(move_comments[2])

    @request_context
    def test_filter_by_author(self):
        user = self.blend_user(name="someone")
        move_comment = self.blend_move_comment(author=user)
        self.blend_move_comment(count=3)

        response = MoveCommentPayload()\
            .get_collection(args={'filter': '[{"name":"author__name","op":"has","val":"%s"}]' % user.name})\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(move_comment)

        self.blend_move_comment(count=3)
        response = MoveCommentPayload()\
            .get_collection(args={'filter': '[{"name":"author__id","op":"has","val":"%s"}]' % user.id})\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(move_comment)

        response = MoveCommentPayload()\
            .get_collection(args={'filter': '[{"name":"author","op":"has","val":{"name":"name","op":"like","val":"some%"}}]'})\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(move_comment)

    @request_context
    def test_filter_by_move(self):
        move_comment = self.blend_move_comment()
        self.blend_move_comment(count=3)

        response = MoveCommentPayload()\
            .get_collection(args={'filter': '[{"name":"move__id","op":"has","val":"%s"}]' % move_comment.move_id})\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(move_comment)

        response = MoveCommentPayload()\
            .get_collection(args={'filter': '[{"name":"move","op":"has","val":{"name":"id","op":"eq","val":"%s"}}]' % move_comment.move_id})\
            .assertCount(1)
        response.data[0].assertHasPublicAttributes(move_comment)

    @request_context
    def test_order_by(self):
        move_comments = self.blend_move_comment(count=3)

        response = MoveCommentPayload()\
            .get_collection(args={'sort': '-id'})\
            .assertCount(3)
        response.data[0].assertHasId(move_comments[2].id)
        response.data[1].assertHasId(move_comments[1].id)
        response.data[2].assertHasId(move_comments[0].id)

    @request_context
    def test_pagination(self):
        move_comments = self.blend_move_comment(count=3)

        response = MoveCommentPayload()\
            .get_collection(args={'page[size]': '1'})\
            .assertCount(3)\
            .assertHasPaginationLinks()
        self.assertEqual(len(response['data']), 1)

        response.data[0].assertHasId(move_comments[0].id)
