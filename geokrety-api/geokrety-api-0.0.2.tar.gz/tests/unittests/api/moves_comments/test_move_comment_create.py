# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_COMMENT_TYPE_COMMENT,
                                         MOVE_COMMENT_TYPE_MISSING,
                                         MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from app.api.helpers.db import safe_query
from geokrety_api_models import MoveComment
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_move_type,
                                                  request_context)
from tests.unittests.utils.payload.move import MovePayload
from tests.unittests.utils.payload.move_comment import MoveCommentPayload
from tests.unittests.utils.static_test_cases import (EMPTY_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES_NO_BLANK,
                                                     UTF8_TEST_CASES)


class TestMoveCommentCreate(BaseTestCase):
    """Test move comment create"""

    @parameterized.expand([
        [None, 401],
        ['admin', 201],
        ['user_1', 201],
        ['user_2', 201],
    ])
    @request_context
    def test_as_(self, username, expected):
        user = getattr(self, username) if username else None
        move = self.blend_move()
        MoveCommentPayload()\
            .set_type(MOVE_COMMENT_TYPE_COMMENT)\
            .set_move(move)\
            .set_comment("Some comment")\
            .post(user=user, code=expected)

    @request_context
    def test_relationships_move_is_mandatory(self):
        MoveCommentPayload().blend()\
            ._del_relationships('move')\
            .set_author(self.user_1)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/relationships/move/data')

    @request_context
    def test_relationships_author_is_optional(self):
        MoveCommentPayload().blend()\
            ._del_relationships('author')\
            .post(user=self.user_1)\
            .assertHasRelationshipAuthorData(self.user_1.id)

    @request_context
    def test_relationships_author_cant_be_overrided(self):
        MoveCommentPayload().blend()\
            .set_author(self.user_2)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/relationships/author/data')

    @request_context
    def test_relationships_author_can_be_overrided_by_admin(self):
        MoveCommentPayload().blend()\
            .set_author(self.user_2)\
            .post(user=self.admin)\
            .assertHasRelationshipAuthorData(self.user_2.id)

    @request_context
    def test_field_comment_is_mandatory(self):
        MoveCommentPayload().blend()\
            ._del_attribute('comment')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/comment')

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_comment_support_utf8(self, comment, expected):
        MoveCommentPayload().blend()\
            .set_comment(comment)\
            .post(user=self.user_1)\
            .assertHasComment(expected)

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_comment_cannot_be_blank(self, comment):
        MoveCommentPayload().blend()\
            .set_comment(comment)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/comment')

    @parameterized.expand(HTML_SUBSET_TEST_CASES_NO_BLANK)
    @request_context
    def test_field_comment_support_html_subset(self, comment, expected):
        MoveCommentPayload().blend()\
            .set_comment(comment)\
            .post(user=self.user_1)\
            .assertHasComment(expected)

    @request_context
    def test_field_type_is_of_type_comment(self):
        MoveCommentPayload().blend()\
            .post(user=self.user_1)\
            .assertHasType(MOVE_COMMENT_TYPE_COMMENT)

    @request_context
    def test_field_type_from_predefined_list(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED)
        payload = MoveCommentPayload().blend(move=move)
        payload.set_type(MOVE_COMMENT_TYPE_COMMENT).post(user=self.user_1)
        payload.set_type(MOVE_COMMENT_TYPE_MISSING).post(user=self.user_1)
        payload.set_type(666).post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/type')

    @request_context
    def test_geokret_id_stored_in_database_for_compatibility_with_legacy(self):
        move = self.blend_move()
        payload = MoveCommentPayload().blend()\
            .set_move(move)\
            .post(user=self.user_1)
        move_comment = safe_query(self, MoveComment, 'id', payload.id, 'id')
        self.assertIsNotNone(move_comment.geokret_id)
        self.assertEqual(move_comment.geokret_id, move.geokret.id)

    @request_context
    def test_geokret_missing_status_computed(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED)
        self.assertFalse(move.geokret.missing)
        MoveCommentPayload()\
            .set_comment("Comment")\
            .set_move(move)\
            .set_type(MOVE_COMMENT_TYPE_MISSING)\
            .post(user=self.user_1)
        self.assertTrue(move.geokret.missing)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, 201],
        [MOVE_TYPE_GRABBED, 422],
        [MOVE_TYPE_COMMENT, 422],
        [MOVE_TYPE_SEEN, 201],
        [MOVE_TYPE_DIPPED, 422],
        [MOVE_TYPE_ARCHIVED, 201],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_geokret_missing_comment_not_accepted_for_some_move_type(self, move_type, expected):
        move = self.blend_move(type=move_type)
        result = MoveCommentPayload().blend()\
            .set_move(move)\
            .set_type(MOVE_COMMENT_TYPE_MISSING)\
            .post(user=self.user_1, code=expected)
        if expected == 422:
            result.assertRaiseJsonApiError('/data/relationships/move/data')
            self.assertEqual(len(move.comments), 0)
            self.assertFalse(move.geokret.missing)
        else:
            self.assertEqual(len(move.comments), 1)
            self.assertTrue(move.geokret.missing)

    @request_context
    def test_missing_cannot_be_posted_on_old_moves(self):
        geokret = self.blend_geokret(created_on_datetime='2019-01-12T22:53:05')
        move = self.blend_move(type=MOVE_TYPE_DROPPED,
                               geokret=geokret,
                               moved_on_datetime='2019-01-12T22:53:21')
        self.blend_move(type=MOVE_TYPE_DROPPED,
                        geokret=geokret,
                        moved_on_datetime='2019-01-12T22:53:43')
        payload = MoveCommentPayload().blend()\
            .set_move(move)\
            .set_type(MOVE_COMMENT_TYPE_MISSING)

        payload.post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/relationships/move')

        payload.set_type(MOVE_COMMENT_TYPE_COMMENT).post(user=self.user_1)

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

        MovePayload(geokret=geokret)\
            .set_type(MOVE_TYPE_DROPPED)\
            .set_coordinates()\
            .set_moved_on_datetime('2019-01-12T23:33:15')\
            .post(user=self.admin)

        MovePayload(geokret=geokret)\
            .set_type(move_type)\
            .set_coordinates()\
            .post(user=self.admin)
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
            .set_type(MOVE_COMMENT_TYPE_MISSING)
        payload.post(user=self.user_1)
        self.assertTrue(geokret.missing)
        payload.post(user=self.user_1)
        self.assertTrue(geokret.missing)
        payload.post(user=self.user_1)
        self.assertTrue(geokret.missing)

    @request_context
    def test_missing_can_be_reported_again_on_new_moves(self):
        geokret = self.blend_geokret(created_on_datetime='2019-01-13T18:02:17')
        move1 = self.blend_move(type=MOVE_TYPE_DROPPED,
                                geokret=geokret,
                                moved_on_datetime='2019-01-13T18:02:57')
        MoveCommentPayload().blend()\
            .set_move(move1)\
            .set_type(MOVE_COMMENT_TYPE_MISSING)\
            .post(user=self.user_1)
        self.assertTrue(geokret.missing)

        move2 = self.blend_move(type=MOVE_TYPE_DROPPED,
                                geokret=geokret,
                                moved_on_datetime='2019-01-13T18:03:26')
        self.assertFalse(geokret.missing)
        MoveCommentPayload().blend()\
            .set_move(move2)\
            .set_type(MOVE_COMMENT_TYPE_MISSING)\
            .post(user=self.user_1)
        self.assertTrue(geokret.missing)
