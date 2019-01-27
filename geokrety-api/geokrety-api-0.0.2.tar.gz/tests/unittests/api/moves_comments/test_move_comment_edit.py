# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_COMMENT_TYPE_COMMENT,
                                         MOVE_COMMENT_TYPE_MISSING,
                                         MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_move_type,
                                                  request_context)
from tests.unittests.utils.payload.move import MovePayload
from tests.unittests.utils.payload.move_comment import MoveCommentPayload
from tests.unittests.utils.static_test_cases import (EMPTY_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES_NO_BLANK,
                                                     UTF8_TEST_CASES)


class TestMoveCommentEdit(BaseTestCase):
    """Test move comment edit"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],  # author
        ['user_2', 403],
    ])
    @request_context
    def test_as_(self, username, expected):
        user = getattr(self, username) if username else None
        move_comment = self.blend_move_comment(author=self.user_1)
        MoveCommentPayload()\
            .set_comment("Some other comment")\
            .patch(move_comment.id, user=user, code=expected)

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],  # GeoKret owner
        ['user_2', 403],
    ])
    @request_context
    def test_geokret_owner_can_edit_comments(self, username, expected):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_1)
        move = self.blend_move(geokret=geokret)
        move_comment = self.blend_move_comment(move=move)
        MoveCommentPayload()\
            .set_comment("Some other comment")\
            .patch(move_comment.id, user=user, code=expected)

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_comment_cannot_be_emptied(self, comment):
        move_comment = self.blend_move_comment()
        MoveCommentPayload()\
            .set_comment(comment)\
            .patch(move_comment.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/comment')

    @parameterized.expand(HTML_SUBSET_TEST_CASES_NO_BLANK)
    @request_context
    def test_field_comment_support_html_subset(self, comment, expected):
        move_comment = self.blend_move_comment()
        MoveCommentPayload()\
            .set_comment(comment)\
            .patch(move_comment.id, user=self.admin)\
            .assertHasComment(expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_comment_support_utf8(self, comment, expected):
        move_comment = self.blend_move_comment()
        MoveCommentPayload()\
            .set_comment(comment)\
            .patch(move_comment.id, user=self.admin)\
            .assertHasComment(expected)

    @request_context
    def test_relationships_author_cant_be_overrided(self):
        move_comment = self.blend_move_comment(author=self.user_1)
        MoveCommentPayload()\
            .set_author(self.user_2)\
            .patch(move_comment.id, user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/relationships/author/data')

    @request_context
    def test_relationships_author_can_be_overrided_by_admin(self):
        move_comment = self.blend_move_comment()
        MoveCommentPayload()\
            .set_author(self.user_2)\
            .patch(move_comment.id, user=self.admin)\
            .assertHasRelationshipAuthorData(self.user_2.id)

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],  # Comment author
        ['user_2', 403],
    ])
    @request_context
    def test_relationships_move_can_be_overrided_by_comment_author(self, username, expected):
        user = getattr(self, username) if username else None
        move_comment = self.blend_move_comment(author=self.user_1)
        move2 = self.blend_move()
        response = MoveCommentPayload()\
            .set_move(move2)\
            .patch(move_comment.id, user=user, code=expected)
        if expected == 200:
            response.assertHasRelationshipMoveData(move2)

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],  # Move author
        ['user_2', 403],
    ])
    @request_context
    def test_relationships_move_can_be_overrided_by_move_author(self, username, expected):
        user = getattr(self, username) if username else None
        move1 = self.blend_move(author=self.user_1)
        move_comment = self.blend_move_comment(move=move1)
        move2 = self.blend_move()
        response = MoveCommentPayload()\
            .set_move(move2)\
            .patch(move_comment.id, user=user, code=expected)
        if expected == 200:
            response.assertHasRelationshipMoveData(move2)

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],  # GeoKret owner
        ['user_2', 403],
    ])
    @request_context
    def test_relationships_move_can_be_overrided_by_geokret_owner(self, username, expected):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_1)
        move1 = self.blend_move(geokret=geokret)
        move_comment = self.blend_move_comment(move=move1)
        move2 = self.blend_move()
        response = MoveCommentPayload()\
            .set_move(move2)\
            .patch(move_comment.id, user=user, code=expected)
        if expected == 200:
            response.assertHasRelationshipMoveData(move2)

    @request_context
    def test_field_type_from_predefined_list(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED)
        move_comment = self.blend_move_comment(move=move, author=self.user_1)
        payload = MoveCommentPayload()
        payload.set_type(MOVE_COMMENT_TYPE_COMMENT)\
            .patch(move_comment.id, user=self.user_1)
        payload.set_type(MOVE_COMMENT_TYPE_MISSING)\
            .patch(move_comment.id, user=self.user_1)
        payload.set_type(666)\
            .patch(move_comment.id, user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/type')

    @request_context
    def test_geokret_missing_status_computed(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED)
        move_comment = self.blend_move_comment(move=move, author=self.user_1)
        self.assertFalse(move.geokret.missing)
        MoveCommentPayload()\
            .set_type(MOVE_COMMENT_TYPE_MISSING)\
            .patch(move_comment.id, user=self.user_1)
        self.assertTrue(move.geokret.missing)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, 200],
        [MOVE_TYPE_GRABBED, 422],
        [MOVE_TYPE_COMMENT, 422],
        [MOVE_TYPE_SEEN, 200],
        [MOVE_TYPE_DIPPED, 422],
        [MOVE_TYPE_ARCHIVED, 200],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_geokret_missing_comment_not_accepted_for_some_move_type(self, move_type, expected):
        move = self.blend_move(type=move_type)
        move_comment = self.blend_move_comment(move=move, type=MOVE_COMMENT_TYPE_COMMENT, author=self.user_1)
        result = MoveCommentPayload()\
            .set_type(MOVE_COMMENT_TYPE_MISSING)\
            .patch(move_comment.id, user=self.user_1, code=expected)
        if expected == 422:
            result.assertRaiseJsonApiError('/data/relationships/move/data')
            self.assertEqual(move_comment.type, MOVE_COMMENT_TYPE_COMMENT)
            self.assertFalse(move.geokret.missing)
        else:
            result.assertHasType(MOVE_COMMENT_TYPE_MISSING)
            self.assertEqual(move_comment.type, MOVE_COMMENT_TYPE_MISSING)
            self.assertTrue(move.geokret.missing)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_GRABBED, False],
        [MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_DIPPED, False],
        [MOVE_TYPE_ARCHIVED, False],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_some_move_type_change_involve_convert_missing_to_comment(self, move_type, expected):
        move = self.blend_move(type=MOVE_TYPE_DROPPED)
        self.blend_move_comment(type=MOVE_COMMENT_TYPE_MISSING,
                                move=move,
                                author=self.user_1)
        self.assertTrue(move.geokret.missing)
        MovePayload()\
            .set_type(move_type)\
            .set_coordinates()\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.geokret.missing, expected)

    @request_context
    def test_missing_cannot_be_posted_on_old_moves(self):
        geokret = self.blend_geokret(created_on_datetime='2019-01-12T22:53:05')
        move1 = self.blend_move(type=MOVE_TYPE_DROPPED,
                                geokret=geokret,
                                moved_on_datetime='2019-01-12T22:53:21')
        move2 = self.blend_move(type=MOVE_TYPE_DROPPED,
                                geokret=geokret,
                                moved_on_datetime='2019-01-12T22:53:43')
        move_comment = self.blend_move_comment(move=move2,
                                               type=MOVE_COMMENT_TYPE_MISSING)
        payload = MoveCommentPayload()
        payload.set_move(move1)\
            .set_type(MOVE_COMMENT_TYPE_MISSING)\
            .patch(move_comment.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/relationships/move')

        payload.set_move(move1)\
            .set_type(MOVE_COMMENT_TYPE_COMMENT)\
            .patch(move_comment.id, user=self.admin)\
            .assertHasRelationshipMoveData(move1)

        move3 = self.blend_move(type=MOVE_TYPE_DROPPED,
                                geokret=geokret,
                                moved_on_datetime='2019-01-12T23:07:03')
        payload.set_move(move3)\
            .set_type(MOVE_COMMENT_TYPE_MISSING)\
            .patch(move_comment.id, user=self.admin)\
            .assertHasRelationshipMoveData(move3)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, False],
        [MOVE_TYPE_GRABBED, False],
        [MOVE_TYPE_COMMENT, True],
        [MOVE_TYPE_SEEN, False],
        [MOVE_TYPE_DIPPED, False],
        [MOVE_TYPE_ARCHIVED, False],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_missing_reset_on_next_move(self, move_type, expected):
        geokret = self.blend_geokret(created_on_datetime='2019-01-12T23:33:08')
        move = self.blend_move(type=MOVE_TYPE_DROPPED,
                               geokret=geokret,
                               moved_on_datetime='2019-01-12T23:33:20')
        self.blend_move_comment(move=move,
                                type=MOVE_COMMENT_TYPE_MISSING)
        self.assertTrue(geokret.missing)

        move1 = MovePayload(geokret=geokret)\
            .set_type(MOVE_TYPE_DROPPED)\
            .set_coordinates()\
            .set_moved_on_datetime('2019-01-12T23:33:15')\
            .post(user=self.admin)
        MovePayload()\
            .set_type(move_type)\
            .set_moved_on_datetime('2019-01-12T23:40:00')\
            .patch(move1.id, user=self.admin)

        self.assertEqual(geokret.missing, expected)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_ARCHIVED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_missing_can_be_reported_multiple_times(self, move_type):
        geokret = self.blend_geokret(created_on_datetime='2019-01-12T23:33:08')
        move = self.blend_move(type=move_type,
                               geokret=geokret,
                               moved_on_datetime='2019-01-12T23:33:20')

        payload = MoveCommentPayload().blend()\
            .set_move(move)\
            .set_type(MOVE_COMMENT_TYPE_COMMENT)
        comment1 = payload.post(user=self.user_1)
        comment2 = payload.post(user=self.user_1)
        comment3 = payload.post(user=self.user_1)

        payload = MoveCommentPayload().set_type(MOVE_COMMENT_TYPE_MISSING)
        payload.patch(comment1.id, user=self.user_1)
        payload.patch(comment2.id, user=self.user_1)
        payload.patch(comment3.id, user=self.user_1)
