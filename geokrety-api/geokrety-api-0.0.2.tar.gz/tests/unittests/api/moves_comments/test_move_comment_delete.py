# -*- coding: utf-8 -*-

from flask import current_app
from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_COMMENT_TYPE_MISSING,
                                         MOVE_TYPE_DROPPED)
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move_comment import MoveCommentPayload


class TestMoveCommentDelete(BaseTestCase):
    """Test move comment delete"""

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
        MoveCommentPayload().delete(move_comment.id, user=user, code=expected)

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],  # GeoKret owner
        ['user_2', 403],
    ])
    @request_context
    def test_geokret_owner_can_delete_comments(self, username, expected):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_1)
        move = self.blend_move(geokret=geokret)
        move_comment = self.blend_move_comment(move=move)
        MoveCommentPayload().delete(move_comment.id, user=user, code=expected)

    @parameterized.expand([
        [True, 200],
        [False, 403],
    ])
    @request_context
    def test_option_geokret_owner_can_delete_comments(self, enable, expected):
        current_app.config['ALLOW_GEOKRET_OWNER_TO_MODERATE_MOVE_COMMENTS'] = enable
        geokret = self.blend_geokret(owner=self.user_1)
        move = self.blend_move(geokret=geokret)
        move_comment = self.blend_move_comment(move=move)
        MoveCommentPayload()\
            .delete(move_comment.id, user=self.user_1, code=expected)
        current_app.config['ALLOW_GEOKRET_OWNER_TO_MODERATE_MOVE_COMMENTS'] = True

    @parameterized.expand([
        [None, 401],
        ['admin', 200],
        ['user_1', 200],  # move author
        ['user_2', 403],
    ])
    @request_context
    def test_move_author_can_delete_comments(self, username, expected):
        user = getattr(self, username) if username else None
        move = self.blend_move(author=self.user_1)
        move_comment = self.blend_move_comment(move=move)
        MoveCommentPayload().delete(move_comment.id, user=user, code=expected)

    @parameterized.expand([
        [True, 200],
        [False, 403],
    ])
    @request_context
    def test_option_move_author_can_moderate_move_comments(self, enable, expected):
        current_app.config['ALLOW_MOVE_AUTHOR_TO_MODERATE_MOVE_COMMENTS'] = enable
        move = self.blend_move(author=self.user_1)
        move_comment = self.blend_move_comment(move=move)
        MoveCommentPayload()\
            .delete(move_comment.id, user=self.user_1, code=expected)
        current_app.config['ALLOW_MOVE_AUTHOR_TO_MODERATE_MOVE_COMMENTS'] = True

    @request_context
    def test_geokret_missing_status_computed(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED)
        move_comment = self.blend_move_comment(move=move, type=MOVE_COMMENT_TYPE_MISSING, author=self.user_1)
        self.assertTrue(move.geokret.missing)
        MoveCommentPayload().delete(move_comment.id, user=self.user_1)
        self.assertFalse(move.geokret.missing)
