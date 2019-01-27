from datetime import datetime, timedelta

from parameterized import parameterized

from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.permissions import (is_date_in_the_future,
                                         is_move_before_geokret_birth,
                                         is_there_a_move_at_that_datetime)
from geokrety_api_models.utilities.const import (MOVE_TYPE_ARCHIVED,
                                                 MOVE_TYPE_COMMENT,
                                                 MOVE_TYPE_DIPPED,
                                                 MOVE_TYPE_DROPPED,
                                                 MOVE_TYPE_GRABBED,
                                                 MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_double_move_type,
                                                  request_context)


class TestPermissions(BaseTestCase):

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_GRABBED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_COMMENT, MOVE_TYPE_DROPPED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_GRABBED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_SEEN, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_DIPPED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_ARCHIVED, False],

        [MOVE_TYPE_SEEN, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_SEEN, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_ARCHIVED, True],
    ], doc_func=custom_name_geokrety_double_move_type)
    @request_context
    def test_is_there_a_move_at_that_datetime__create(self, move_type_1, move_type_2, expected):
        geokret = self.blend_geokret()
        self.blend_move(geokret=geokret,
                        type=move_type_1,
                        moved_on_datetime="2019-01-22T22:16:01")

        move_kwargs = {
            "geokret": geokret.id,
            "type": move_type_2,
            "moved_on_datetime": "2019-01-22T22:16:01",
        }

        if expected:
            is_there_a_move_at_that_datetime(None, (), {}, (), **move_kwargs)
        else:
            with self.assertRaises(UnprocessableEntity):
                is_there_a_move_at_that_datetime(None, (), {}, (), **move_kwargs)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_GRABBED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_COMMENT, MOVE_TYPE_DROPPED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_GRABBED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_SEEN, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_DIPPED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_ARCHIVED, False],

        [MOVE_TYPE_SEEN, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_SEEN, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_ARCHIVED, True],
    ], doc_func=custom_name_geokrety_double_move_type)
    @request_context
    def test_is_there_a_move_at_that_datetime__edit_move_type(self, move_type_1, move_type_2, expected):
        geokret = self.blend_geokret()
        move = self.blend_move(geokret=geokret,
                               type=MOVE_TYPE_DROPPED,
                               moved_on_datetime="2019-01-22T22:16:01")
        self.blend_move(geokret=geokret,
                        type=move_type_1,
                        moved_on_datetime="2019-01-23T17:01:33")

        move_kwargs = {
            "id": move.id,
            "type": move_type_2,
            "moved_on_datetime": "2019-01-23T17:01:33",
        }

        if expected:
            is_there_a_move_at_that_datetime(None, (), {}, (), **move_kwargs)
        else:
            with self.assertRaises(UnprocessableEntity):
                is_there_a_move_at_that_datetime(None, (), {}, (), **move_kwargs)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_DROPPED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_GRABBED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_GRABBED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_COMMENT, MOVE_TYPE_DROPPED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_GRABBED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_SEEN, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_DIPPED, False],
        [MOVE_TYPE_COMMENT, MOVE_TYPE_ARCHIVED, False],

        [MOVE_TYPE_SEEN, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_SEEN, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_SEEN, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_DIPPED, MOVE_TYPE_ARCHIVED, True],

        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_DIPPED, True],
        [MOVE_TYPE_ARCHIVED, MOVE_TYPE_ARCHIVED, True],
    ], doc_func=custom_name_geokrety_double_move_type)
    @request_context
    def test_is_there_a_move_at_that_datetime__edit_geokret(self, move_type_1, move_type_2, expected):
        move1 = self.blend_move(type=MOVE_TYPE_DROPPED,
                                moved_on_datetime="2019-01-22T22:16:01")
        move2 = self.blend_move(type=move_type_1,
                                moved_on_datetime="2019-01-23T17:01:33")

        move_kwargs = {
            "id": move1.id,
            "geokret": move2.geokret_id,
            "type": move_type_2,
            "moved_on_datetime": "2019-01-23T17:01:33",
        }

        if expected:
            is_there_a_move_at_that_datetime(None, (), {}, (), **move_kwargs)
        else:
            with self.assertRaises(UnprocessableEntity):
                is_there_a_move_at_that_datetime(None, (), {}, (), **move_kwargs)

    @request_context
    def test_is_move_before_geokret_birth__create(self):
        def blend(moved_on_datetime):
            return {
                "geokret_id": geokret.id,
                "moved_on_datetime": datetime.strptime(moved_on_datetime, '%Y-%m-%dT%H:%M:%S'),
            }

        geokret = self.blend_geokret(created_on_datetime="2019-01-23T17:50:48")
        is_move_before_geokret_birth(None, (), {}, (), **blend("2019-01-23T17:50:47"))
        with self.assertRaises(UnprocessableEntity):
            is_move_before_geokret_birth(None, (), {}, (), **blend("2019-01-23T17:50:48"))
        with self.assertRaises(UnprocessableEntity):
            is_move_before_geokret_birth(None, (), {}, (), **blend("2019-01-23T17:50:49"))

    @request_context
    def test_is_move_before_geokret_birth__edit_move_datetime(self):
        def blend(moved_on_datetime):
            return {
                "id": move1.id,
                "moved_on_datetime": datetime.strptime(moved_on_datetime, '%Y-%m-%dT%H:%M:%S'),
            }

        geokret = self.blend_geokret(created_on_datetime="2019-01-23T18:17:17")
        move1 = self.blend_move(geokret=geokret,
                                type=MOVE_TYPE_DROPPED,
                                moved_on_datetime="2019-01-23T18:17:17")
        is_move_before_geokret_birth(None, (), {}, (), **blend("2019-01-23T18:17:00"))
        with self.assertRaises(UnprocessableEntity):
            is_move_before_geokret_birth(None, (), {}, (), **blend("2019-01-23T18:17:17"))
        with self.assertRaises(UnprocessableEntity):
            is_move_before_geokret_birth(None, (), {}, (), **blend("2019-01-23T18:17:18"))

    @request_context
    def test_is_move_before_geokret_birth__edit_geokret(self):
        def blend(geokret):
            return {
                "id": move1.id,
                "geokret_id": geokret.id,
            }

        geokret1 = self.blend_geokret(created_on_datetime="2019-01-22T18:17:17")
        geokret2 = self.blend_geokret(created_on_datetime="2019-01-23T18:17:17")
        geokret3 = self.blend_geokret(created_on_datetime="2019-01-21T18:17:17")
        move1 = self.blend_move(geokret=geokret1,
                                type=MOVE_TYPE_DROPPED,
                                moved_on_datetime="2019-01-22T18:17:17")
        is_move_before_geokret_birth(None, (), {}, (), **blend(geokret2))
        with self.assertRaises(UnprocessableEntity):
            is_move_before_geokret_birth(None, (), {}, (), **blend(geokret3))

    @request_context
    def test_is_date_in_the_future__create(self):
        def blend(date_time):
            return {
                "date_time": date_time,
            }

        is_date_in_the_future(None, (), {}, (), **blend(datetime.utcnow() + timedelta(seconds=1)))
        with self.assertRaises(UnprocessableEntity):
            is_date_in_the_future(None, (), {}, (), **blend(datetime.utcnow()))
