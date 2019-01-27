# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED)
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.geokret import GeokretPayload
from tests.unittests.utils.payload.move import MovePayload


class TestMoveCreateArchive(BaseTestCase):
    """Test Move create Archive"""

    @parameterized.expand([
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_move_create_archive_as(self, username):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret)\
            .post(user=user, code=403)

    @parameterized.expand([
        ['user_1'],
        ['admin'],
    ])
    @request_context
    def test_move_create_archive_as_owner(self, username):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_1)
        MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret)\
            .post(user=user)
        self.assertEqual(geokret.archived, True)

    @request_context
    def test_archive_date_must_be_provided(self):
        geokret = self.blend_geokret(owner=self.user_1)
        MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret)\
            ._del_attribute('moved-on-datetime')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @request_context
    def test_archive_date_must_not_be_before_born_date(self):
        geokret = self.blend_geokret(owner=self.user_1, created_on_datetime='2018-12-29T16:33:46')
        MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret)\
            .set_moved_on_datetime('2018-12-29T16:33:00')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @request_context
    def test_archive_date_must_not_be_the_future(self):
        geokret = self.blend_geokret(owner=self.user_1)
        MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret)\
            .set_moved_on_datetime(datetime.now() + timedelta(hours=6))\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @request_context
    def test_a_comment_may_be_provided(self):
        geokret = self.blend_geokret(owner=self.user_1)
        MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret)\
            .set_comment("Some comment")\
            .post(user=self.user_1)

    @request_context
    def test_moves_can_continue_after_archive(self):
        geokret = self.blend_geokret(owner=self.user_1, created_on_datetime='2018-12-29T16:40:06')
        MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret)\
            .set_moved_on_datetime('2018-12-29T16:40:14')\
            .post(user=self.user_1)
        self.assertTrue(geokret.archived)

        MovePayload(MOVE_TYPE_COMMENT, geokret=geokret)\
            .set_moved_on_datetime('2018-12-29T16:40:33')\
            .set_comment("This GeoKret is not dead")\
            .post(user=self.user_1)
        self.assertTrue(geokret.archived)

        MovePayload(MOVE_TYPE_DIPPED, geokret=geokret)\
            .set_moved_on_datetime('2018-12-29T16:40:41')\
            .set_coordinates()\
            .set_comment("Will continue it's journey")\
            .post(user=self.user_1)
        self.assertFalse(geokret.archived)

    @request_context
    def test_archived_geokret_must_not_be_shown_in_cache_details(self):
        geokret_1 = self.blend_geokret(owner=self.user_1, created_on_datetime='2018-12-29T16:43:28')
        MovePayload(MOVE_TYPE_DROPPED, geokret=geokret_1)\
            .set_moved_on_datetime('2018-12-29T16:44:57')\
            .set_coordinates()\
            .set_waypoint('ABC123')\
            .post(user=self.user_1)

        geokret_2 = self.blend_geokret(owner=self.user_1, created_on_datetime='2018-12-29T16:43:28')
        MovePayload(MOVE_TYPE_DROPPED, geokret=geokret_2)\
            .set_moved_on_datetime('2018-12-29T16:44:57')\
            .set_coordinates()\
            .set_waypoint('ABC123')\
            .post(user=self.user_1)

        GeokretPayload()\
            .get_collection(args={'filter': '[{"name":"last_position","op":"has","val":{"name":"waypoint","op":"eq","val":"ABC123"}}]'})\
            .assertCount(2)

        MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret_1)\
            .set_moved_on_datetime('2018-12-29T16:45:03')\
            .post(user=self.user_1)

        GeokretPayload()\
            .get_collection(args={'filter': '[{"name":"last_position__waypoint","op":"has","val":"ABC123"}]'})\
            .assertCount(1)
