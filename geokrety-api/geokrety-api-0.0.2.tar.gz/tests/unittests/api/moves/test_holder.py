# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_TYPE_COMMENT, MOVE_TYPE_DIPPED,
                                         MOVE_TYPE_DROPPED, MOVE_TYPE_GRABBED,
                                         MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_double_move_type,
                                                  request_context)
from tests.unittests.utils.payload.move import MovePayload


class TestHolder(BaseTestCase):
    """Test Holder"""

    @parameterized.expand([
        [MOVE_TYPE_GRABBED, MOVE_TYPE_GRABBED, 'user_1', 'user_2'],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_DROPPED, 'user_1', None],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_COMMENT, 'user_1', 'user_1'],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN, 'user_1', None],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_DIPPED, 'user_1', 'user_2'],

        [MOVE_TYPE_DROPPED, MOVE_TYPE_GRABBED, None, 'user_2'],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_DROPPED, None, None],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_COMMENT, None, None],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_SEEN, None, None],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_DIPPED, None, 'user_2'],

        [MOVE_TYPE_COMMENT, MOVE_TYPE_GRABBED, None, 'user_2'],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_DROPPED, None, None],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_COMMENT, None, None],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_SEEN, None, None],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_DIPPED, None, 'user_2'],

        [MOVE_TYPE_SEEN, MOVE_TYPE_GRABBED, None, 'user_2'],
        [MOVE_TYPE_SEEN, MOVE_TYPE_DROPPED, None, None],
        [MOVE_TYPE_SEEN, MOVE_TYPE_COMMENT, None, None],
        [MOVE_TYPE_SEEN, MOVE_TYPE_SEEN, None, None],
        [MOVE_TYPE_SEEN, MOVE_TYPE_DIPPED, None, 'user_2'],

        [MOVE_TYPE_DIPPED, MOVE_TYPE_GRABBED, 'user_1', 'user_2'],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED, 'user_1', None],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_COMMENT, 'user_1', 'user_1'],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_SEEN, 'user_1', None],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_DIPPED, 'user_1', 'user_2'],
    ], doc_func=custom_name_geokrety_double_move_type)
    @request_context
    def test_holder_must_be_updated(self, move_type1, move_type2, username1, username2):
        user_id1 = getattr(self, username1).id if username1 else None
        user_id2 = getattr(self, username2).id if username2 else None
        geokret = self.blend_geokret(created_on_datetime="2018-10-11T20:13:35")

        MovePayload(move_type1, geokret=geokret, moved_on_datetime="2018-10-11T21:49:55")\
            .set_coordinates()\
            .post(user=self.user_1)

        MovePayload(MOVE_TYPE_COMMENT, geokret=geokret, moved_on_datetime="2018-10-11T23:10:53")\
            .post(user=self.user_2)
        self.assertEqual(geokret.holder_id, user_id1)

        MovePayload(move_type2, geokret=geokret, moved_on_datetime="2018-10-11T23:10:55")\
            .set_coordinates()\
            .post(user=self.user_2)
        self.assertEqual(geokret.holder_id, user_id2)
