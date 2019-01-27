# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_TYPE_COMMENT, MOVE_TYPE_DIPPED,
                                         MOVE_TYPE_DROPPED, MOVE_TYPE_GRABBED,
                                         MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_move_type,
                                                  request_context)
from tests.unittests.utils.payload.move import MovePayload
from tests.unittests.utils.static_test_cases import (HTML_SUBSET_TEST_CASES,
                                                     UTF8_TEST_CASES)


class TestMoveEdit(BaseTestCase):
    """Test Move edit"""

    @parameterized.expand([
        [None, 401],
        ['admin', 200],  # Admin
        ['user_1', 200],  # Author
        ['user_2', 403],
        ['user_0', 200],  # GeoKret owner
    ])
    @request_context
    def test_moves_edit_is_forbidden_as(self, username, expected):
        self.user_0 = self.blend_user()
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_0)
        move = self.blend_move(type=MOVE_TYPE_DIPPED, geokret=geokret, author=self.user_1)
        response = MovePayload()\
            .set_id(move.id)\
            .set_coordinates()\
            .set_comment("Some new comment")\
            .patch(move.id, user=user, code=expected)
        if expected == 200:
            response.assertHasAttribute('comment', "Some new comment")
        else:
            self.assertNotEqual(move.comment, "Some new comment")

    @request_context
    def test_no_need_to_include_coordinates_if_last_move_has_coordinates(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED, latitude=43.78, longitude=7.06)
        MovePayload(MOVE_TYPE_DIPPED)\
            .set_id(move.id)\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_DIPPED)

    @request_context
    def test_must_include_coordinates_if_missing_from_last_move(self):
        move = self.blend_move(type=MOVE_TYPE_GRABBED)
        payload = MovePayload(MOVE_TYPE_DIPPED)\
            .set_id(move.id)

        payload.patch(move.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/latitude')\
            .assertRaiseJsonApiError('/data/attributes/longitude')

        payload.set_coordinates()\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_DIPPED)

    @request_context
    def test_coordinates_are_optionnal_for_grab(self):
        move = self.blend_move(type=MOVE_TYPE_DIPPED)
        payload = MovePayload(MOVE_TYPE_GRABBED)\
            .set_id(move.id)

        payload.patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_GRABBED)

        payload.set_coordinates()\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_GRABBED)

    @request_context
    def test_convert_to_dropped(self):
        move = self.blend_move(type=MOVE_TYPE_GRABBED)
        payload = MovePayload(MOVE_TYPE_DROPPED)\
            .set_id(move.id)

        payload.patch(move.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/latitude')\
            .assertRaiseJsonApiError('/data/attributes/longitude')

        payload.set_coordinates()\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_DROPPED)
        self.assertEqual(float(move.latitude), 43.78)
        self.assertEqual(float(move.longitude), 7.06)

    @request_context
    def test_convert_to_grabbed(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED, latitude=43.78, longitude=7.06)
        payload = MovePayload(MOVE_TYPE_GRABBED)\
            .set_id(move.id)

        payload.patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_GRABBED)
        self.assertEqual(float(move.latitude), 43.78)
        self.assertEqual(float(move.longitude), 7.06)

        payload.set_coordinates(None, None)\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_GRABBED)
        self.assertIsNone(move.latitude)
        self.assertIsNone(move.longitude)

    @request_context
    def test_convert_to_comment(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED, latitude=43.78, longitude=7.06)
        MovePayload(MOVE_TYPE_COMMENT)\
            .set_id(move.id)\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_COMMENT)
        self.assertIsNone(move.latitude)
        self.assertIsNone(move.longitude)

    @request_context
    def test_convert_to_seen(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED, latitude=43.78, longitude=7.06)
        payload = MovePayload(MOVE_TYPE_SEEN)\
            .set_id(move.id)

        payload.patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_SEEN)
        self.assertEqual(float(move.latitude), 43.78)
        self.assertEqual(float(move.longitude), 7.06)

        payload._set_attribute('latitude', 43.79)\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_SEEN)
        self.assertEqual(float(move.latitude), 43.79)
        self.assertEqual(float(move.longitude), 7.06)

        payload.set_coordinates(None, None)\
            .patch(move.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/latitude')\
            .assertRaiseJsonApiError('/data/attributes/longitude')

    @request_context
    def test_convert_to_dipped(self):
        move = self.blend_move(type=MOVE_TYPE_DROPPED, latitude=43.78, longitude=7.06)
        payload = MovePayload(MOVE_TYPE_DIPPED)\
            .set_id(move.id)

        payload.patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_DIPPED)
        self.assertEqual(float(move.latitude), 43.78)
        self.assertEqual(float(move.longitude), 7.06)

        payload.set_coordinates(None, None)\
            .patch(move.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/latitude')\
            .assertRaiseJsonApiError('/data/attributes/longitude')

    @request_context
    def test_author_change_restrictions(self):
        move = self.blend_move(type=MOVE_TYPE_GRABBED, author=self.user_1)
        payload = MovePayload(MOVE_TYPE_GRABBED)\
            .set_id(move.id)\
            .set_author(self.user_2.id)

        payload.patch(move.id, user=self.user_1, code=403)\
            .assertRaiseJsonApiError('/data/relationships/author')

        payload.patch(move.id, user=self.admin)
        self.assertEqual(move.author.id, self.user_2.id)

    @request_context
    def test_geokret_relation_can_be_changed_only_by_admin(self):
        geokret = self.blend_geokret()
        move = self.blend_move(type=MOVE_TYPE_GRABBED, author=self.user_1)
        payload = MovePayload(MOVE_TYPE_GRABBED)\
            .set_id(move.id)\
            .set_geokret(geokret.id)

        payload.patch(move.id, user=self.user_1, code=403)\
            .assertRaiseJsonApiError('/data/relationships/geokret')

        payload.patch(move.id, user=self.admin)
        self.assertEqual(move.geokret.id, geokret.id)

    @request_context
    def test_from_non_authenticated_move_type_need_tracking_code(self):
        move = self.blend_move(type=MOVE_TYPE_COMMENT)
        payload = MovePayload(MOVE_TYPE_GRABBED)\
            .set_id(move.id)

        payload.patch(move.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/tracking-code')

        payload.set_tracking_code(move.geokret.tracking_code)\
            .patch(move.id, user=self.admin)
        self.assertEqual(move.type, MOVE_TYPE_GRABBED)

    @request_context
    def test_geokret_can_be_changed_via_tracking_code(self):
        geokret = self.blend_geokret()
        move = self.blend_move(type=MOVE_TYPE_GRABBED, author=self.user_1)
        MovePayload(MOVE_TYPE_GRABBED)\
            .set_id(move.id)\
            .set_tracking_code(geokret.tracking_code)\
            .patch(move.id, user=self.user_1)\
            .assertHasRelationshipGeokretData(geokret.id)

    @request_context
    def test_move_datetime_cannot_be_before_geokret_birth(self):
        geokret = self.blend_geokret(created_on_datetime='2018-12-28T15:25:56')
        move = self.blend_move(type=MOVE_TYPE_GRABBED, geokret=geokret, author=self.user_1)

        payload = MovePayload(MOVE_TYPE_GRABBED)\
            .set_id(move.id)\
            .set_moved_on_datetime('2018-12-28T14:00:00')

        payload.patch(move.id, user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

        payload.set_moved_on_datetime(geokret.created_on_datetime)\
            .patch(move.id, user=self.user_1)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_on_datetime_must_not_be_in_the_future(self, move_type):
        geokret = self.blend_geokret(created_on_datetime='2019-01-24T18:24:31')
        move = self.blend_move(type=MOVE_TYPE_GRABBED, geokret=geokret,
                               moved_on_datetime='2019-01-24T18:26:42')

        payload = MovePayload(MOVE_TYPE_DIPPED)\
            .set_id(move.id)\
            .set_coordinates()
        payload.set_moved_on_datetime(datetime.utcnow() - timedelta(hours=1))\
            .patch(move.id, user=self.admin)
        payload.set_moved_on_datetime(datetime.utcnow() + timedelta(hours=6))\
            .patch(move.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @request_context
    def test_move_datetime_same_as_another_move(self):
        geokret = self.blend_geokret(created_on_datetime='2018-12-28T16:26:16')
        move_1 = self.blend_move(type=MOVE_TYPE_GRABBED, geokret=geokret,
                                 author=self.user_1, moved_on_datetime='2018-12-28T16:26:49')
        move_2 = self.blend_move(type=MOVE_TYPE_GRABBED, geokret=geokret,
                                 author=self.user_1, moved_on_datetime='2018-12-28T16:26:58')

        payload = MovePayload(MOVE_TYPE_DIPPED)\
            .set_id(move_2.id)\
            .set_coordinates()\
            .set_moved_on_datetime(move_2.moved_on_datetime)
        payload.patch(move_2.id, user=self.user_1)

        payload.set_moved_on_datetime(move_1.moved_on_datetime)\
            .patch(move_2.id, user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @parameterized.expand(HTML_SUBSET_TEST_CASES)
    @request_context
    def test_move_field_comment_accept_html_subset(self, comment, expected):
        geokret = self.blend_geokret()
        move = self.blend_move(type=MOVE_TYPE_GRABBED, geokret=geokret, author=self.user_1)
        MovePayload(MOVE_TYPE_GRABBED, geokret=geokret)\
            .set_id(move.id)\
            .set_comment(comment)\
            .patch(move.id, user=self.user_1)\
            .assertHasAttribute('comment', expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_move_field_comment_accept_unicode(self, comment, expected):
        geokret = self.blend_geokret()
        move = self.blend_move(type=MOVE_TYPE_GRABBED, geokret=geokret, author=self.user_1)
        MovePayload(MOVE_TYPE_GRABBED, geokret=geokret)\
            .set_id(move.id)\
            .set_comment(comment)\
            .patch(move.id, user=self.user_1)\
            .assertHasAttribute('comment', expected)

    @request_context
    def test_altitude_and_country_is_computed_and_not_overridable(self):
        geokret = self.blend_geokret()
        move = self.blend_move(type=MOVE_TYPE_GRABBED,
                               geokret=geokret, author=self.user_1)
        MovePayload(MOVE_TYPE_GRABBED, geokret=geokret)\
            .set_id(move.id)\
            .set_coordinates(52.07567, 9.35367)\
            ._set_attribute('altitude', 666)\
            ._set_attribute('country', 'PL')\
            .patch(move.id, user=self.user_1)\
            .assertHasAttribute('altitude', 126)\
            .assertHasAttribute('country', 'DE')

    @request_context
    def test_distance_is_reevaluated_for_new_and_old_geokrety(self):
        geokret_1 = self.blend_geokret(created_on_datetime='2018-12-29T10:52:00')
        geokret_2 = self.blend_geokret(created_on_datetime='2018-12-29T10:52:00')

        self.blend_move(type=MOVE_TYPE_DIPPED, geokret=geokret_1,
                        author=self.user_1,
                        latitude=43.704233, longitude=6.869833,
                        moved_on_datetime='2018-12-29T10:52:06')
        self.blend_move(type=MOVE_TYPE_DIPPED, geokret=geokret_2,
                        author=self.user_1,
                        latitude=43.704233, longitude=6.869833,
                        moved_on_datetime='2018-12-29T10:52:06')

        move = self.blend_move(type=MOVE_TYPE_DIPPED, geokret=geokret_1,
                               author=self.user_1,
                               latitude=43.6792, longitude=6.852933,
                               moved_on_datetime='2018-12-29T10:52:22')

        # Change coordinates
        MovePayload(MOVE_TYPE_DIPPED)\
            .set_id(move.id)\
            .set_coordinates(52.07567, 9.35367)\
            .patch(move.id, user=self.user_1)\
            .assertHasAttribute('distance', 949)
        self.assertEqual(geokret_1.distance, 949)

        # Change GeoKret
        MovePayload(MOVE_TYPE_DIPPED)\
            .set_id(move.id)\
            .set_tracking_code(geokret_2.tracking_code)\
            .patch(move.id, user=self.user_1)\
            .assertHasAttribute('distance', 949)
        self.assertEqual(geokret_1.distance, 0)
        self.assertEqual(geokret_2.distance, 949)
