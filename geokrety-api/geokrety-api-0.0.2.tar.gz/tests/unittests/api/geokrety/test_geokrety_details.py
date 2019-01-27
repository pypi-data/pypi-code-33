# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_move_type,
                                                  request_context)
from tests.unittests.utils.payload.geokret import GeokretPayload
from tests.unittests.utils.payload.move import MovePayload


class TestGeokretDetails(BaseTestCase):
    """Test GeoKrety details"""

    @parameterized.expand([
        [None],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_has_normal_attributes_as_(self, username):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret()
        GeokretPayload()\
            .get(geokret.id, user=user)\
            .assertHasPublicAttributes(geokret)\
            .assertHasTrackingCode(None)

    @request_context
    def test_has_private_attributes_as_admin(self):
        geokret = self.blend_geokret()
        GeokretPayload()\
            .get(geokret.id, user=self.admin)\
            .assertHasPublicAttributes(geokret)\
            .assertHasTrackingCode(geokret.tracking_code)

    @request_context
    def test_has_tracking_code_as_owner(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .get(geokret.id, user=self.user_1)\
            .assertHasTrackingCode(geokret.tracking_code)

    @request_context
    def test_has_tracking_code_as_holder(self):
        geokret = self.blend_geokret(holder=self.user_1)
        GeokretPayload()\
            .get(geokret.id, user=self.user_1)\
            .assertHasTrackingCode(geokret.tracking_code)

    @request_context
    def test_unexistent_geokret(self):
        GeokretPayload()\
            .get(666)\
            .assertDataIsNone()

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_ARCHIVED, True],
        [MOVE_TYPE_DIPPED, True],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_has_tracking_code_when_user_has_touched(self, move_type, expected):
        geokret = self.blend_geokret(created_on_datetime="2018-09-18T23:37:01")
        self.blend_move(geokret=geokret, author=self.user_1, type=move_type,
                        moved_on_datetime="2018-09-18T23:37:02")
        self.blend_move(geokret=geokret, author=self.user_2, type=MOVE_TYPE_GRABBED,
                        moved_on_datetime="2018-09-18T23:37:03")
        response = GeokretPayload().get(geokret.id, user=self.user_1)
        if expected:
            response.assertHasTrackingCode(geokret.tracking_code)
        else:
            response.assertHasTrackingCode(None)

    @request_context
    def test_sparse_fieldset(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .get(geokret.id, user=self.user_1, args={'fields[geokret]': 'name,description'})\
            .assertHasAttribute('name', geokret.name)\
            .assertHasAttribute('description', geokret.description)\
            .assertAttributeNotPresent('missing')\
            .assertAttributeNotPresent('caches-count')\
            .assertAttributeNotPresent('tracking-code')

    @parameterized.expand([
        [None, False],
        ['admin', True],
        ['user_1', True],  # Owner
        ['user_2', False],
    ])
    @request_context
    def test_sparse_fieldset_has_tracking_code(self, username, expected):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_1)
        response = GeokretPayload()\
            .get(geokret.id, user=user, args={'fields[geokret]': 'tracking_code'})
        if expected:
            response.assertHasTrackingCode(geokret.tracking_code)
        else:
            response.assertHasTrackingCode(None)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_ARCHIVED, True],
        [MOVE_TYPE_DIPPED, True],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_sparse_fieldset_has_tracking_code_when_user_has_touched(self, move_type, expected):
        geokret = self.blend_geokret(created_on_datetime="2018-09-20T23:15:30")
        self.blend_move(geokret=geokret, author=self.user_1, type=move_type,
                        moved_on_datetime="2018-09-20T23:15:31")
        self.blend_move(geokret=geokret, author=self.user_2, type=MOVE_TYPE_GRABBED,
                        moved_on_datetime="2018-09-20T23:15:32")
        response = GeokretPayload()\
            .get(geokret.id, user=self.user_1, args={'fields[geokret]': 'tracking_code'})
        if expected:
            response.assertHasTrackingCode(geokret.tracking_code)
        else:
            response.assertHasTrackingCode(None)

    @request_context
    def test_has_relationships_owner_data(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .get(geokret.id)\
            .assertHasRelationshipOwnerData(geokret.owner_id)

    @request_context
    def test_has_relationships_holder_data(self):
        geokret = self.blend_geokret(holder=self.user_2)
        GeokretPayload()\
            .get(geokret.id)\
            .assertHasRelationshipHolderData(geokret.holder_id)

    @request_context
    def test_has_relationships_last_position_data(self):
        geokret = self.blend_geokret()
        move = MovePayload(MOVE_TYPE_DROPPED, geokret=geokret)\
            .set_coordinates()\
            .post(user=self.user_1)
        GeokretPayload()\
            .get(geokret.id)\
            .assertHasRelationshipLastPositionData(move.id)

    @request_context
    def test_has_relationships_last_move_data(self):
        geokret = self.blend_geokret()
        move = MovePayload(MOVE_TYPE_GRABBED, geokret=geokret)\
            .post(user=self.user_1)
        GeokretPayload()\
            .get(geokret.id)\
            .assertHasRelationshipLastMoveData(move.id)

    @request_context
    def test_has_relationships_moves_data(self):
        geokret = self.blend_geokret()
        moves = self.blend_move(count=5, geokret=geokret, type=MOVE_TYPE_GRABBED)
        GeokretPayload()\
            .get(geokret.id, args={'include': 'moves'})\
            .assertHasRelationshipMovesDatas(moves)

    @request_context
    def test_check_archived_attribute(self):
        geokret = self.blend_geokret(created_on_datetime="2018-12-29T21:39:13")
        GeokretPayload().get(geokret.id).assertHasAttribute('archived', False)

        self.blend_move(geokret=geokret, author=self.user_1, type=MOVE_TYPE_GRABBED,
                        moved_on_datetime="2018-12-29T21:40:39")
        GeokretPayload().get(geokret.id).assertHasAttribute('archived', False)

        self.blend_move(geokret=geokret, author=self.user_1, type=MOVE_TYPE_ARCHIVED,
                        moved_on_datetime="2018-12-29T21:40:45")
        GeokretPayload().get(geokret.id).assertHasAttribute('archived', True)

        self.blend_move(geokret=geokret, author=self.user_1, type=MOVE_TYPE_GRABBED,
                        moved_on_datetime="2018-12-29T21:51:27")
        GeokretPayload().get(geokret.id).assertHasAttribute('archived', False)
