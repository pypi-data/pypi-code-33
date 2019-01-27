# -*- coding: utf-8 -*-

from mixer.backend.flask import mixer
from parameterized import parameterized

from app.api.helpers.data_layers import MOVE_TYPE_DIPPED
from app.models import db
from geokrety_api_models import Move
from geokrety_api_models.utilities.move_tasks import update_move_distances
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.move import MovePayload


class TestMoveDelete(BaseTestCase):
    """Test Move delete"""

    def _blend(self):
        """Create mocked Moves"""
        self.geokret = self.blend_geokret(created_on_datetime='2018-12-27T23:20:18')
        self.move_1 = mixer.blend(Move, type=MOVE_TYPE_DIPPED, geokret=self.geokret,
                                  moved_on_datetime="2018-12-27T23:38:33",
                                  latitude=43.704233, longitude=6.869833)
        self.move_2 = mixer.blend(Move, type=MOVE_TYPE_DIPPED, geokret=self.geokret,
                                  moved_on_datetime="2018-12-27T23:39:06",
                                  latitude=43.6792, longitude=6.852933)
        self.move_3 = mixer.blend(Move, type=MOVE_TYPE_DIPPED, geokret=self.geokret,
                                  moved_on_datetime="2018-12-27T23:41:29",
                                  latitude=43.701767, longitude=6.84085)
        self.move_4 = mixer.blend(Move, type=MOVE_TYPE_DIPPED, geokret=self.geokret,
                                  moved_on_datetime="2018-12-27T23:42:15",
                                  latitude=43.693633, longitude=6.860933)
        update_move_distances(db.session, self.geokret.id)

    @parameterized.expand([
        [None, 401],
        ['admin', 200],  # Admin
        ['user_1', 200],  # Author
        ['user_2', 403],
        ['user_0', 200],  # GeoKret owner
    ])
    @request_context
    def test_moves_delete_is_forbidden_as(self, username, expected):
        self.user_0 = self.blend_user()
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_0)
        move = self.blend_move(geokret=geokret, author=self.user_1)
        MovePayload().delete(move.id, user=user, code=expected)

    @request_context
    def test_moves_delete_distance_is_reevaluated_last_move(self):
        self._blend()
        MovePayload().delete(self.move_4.id, user=self.admin)
        self.assertEqual(self.geokret.distance, 6)

    @request_context
    def test_moves_delete_distance_is_reevaluated_intermediate_moves(self):
        self._blend()
        MovePayload().delete(self.move_2.id, user=self.admin)
        MovePayload().delete(self.move_3.id, user=self.admin)
        self.assertEqual(self.geokret.distance, 1)

    @request_context
    def test_moves_delete_distance_is_reevaluated_first_move(self):
        self._blend()
        MovePayload().delete(self.move_1.id, user=self.admin)
        self.assertEqual(self.geokret.distance, 5)
