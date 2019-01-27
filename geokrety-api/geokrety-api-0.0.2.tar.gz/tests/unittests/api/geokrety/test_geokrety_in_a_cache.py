# -*- coding: utf-8 -*-

from app.api.helpers.data_layers import (MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED)
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.geokret import GeokretyInCachePayload
from tests.unittests.utils.payload.move import MovePayload


class TestGeokretyInACacheCollection(BaseTestCase):
    """Test GeoKrety in a cache collection"""

    @request_context
    def test_missing_paramters(self):
        payload = GeokretyInCachePayload()

        payload.get_collection(code=422, args={})\
            .assertRaiseJsonApiError('/argument/[waypoint or latitude-longitude]')

        payload.get_collection(code=422, args={'latitude': ''})\
            .assertRaiseJsonApiError('/argument/[waypoint or latitude-longitude]')

        payload.get_collection(code=422, args={'longitude': ''})\
            .assertRaiseJsonApiError('/argument/[waypoint or latitude-longitude]')

        payload.get_collection(code=422, args={'latitude': '', 'longitude': ''})\
            .assertRaiseJsonApiError('/argument/[waypoint or latitude-longitude]')

        payload.get_collection(code=422, args={'latitude': 'A', 'longitude': 'B'})\
            .assertRaiseJsonApiError('/argument/latitude')

        payload.get_collection(code=422, args={'latitude': '1', 'longitude': 'B'})\
            .assertRaiseJsonApiError('/argument/longitude')

        payload.get_collection(code=422, args={'latitude': '360', 'longitude': '360'})\
            .assertRaiseJsonApiError('/argument/latitude')

        payload.get_collection(args={'latitude': '52.07567', 'longitude': '9.35367'})

        payload.get_collection(code=422, args={'waypoint': ''})\
            .assertRaiseJsonApiError('/argument/waypoint')

    @request_context
    def test_search_by_waypoint(self):
        geokret = self.blend_geokret(created_on_datetime="2018-12-30T12:56:31")
        geokret2 = self.blend_geokret(created_on_datetime="2018-12-30T12:56:31")

        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(0)

        MovePayload(MOVE_TYPE_COMMENT, geokret=geokret)\
            .set_moved_on_datetime("2018-12-30T12:57:16")\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(0)

        MovePayload(MOVE_TYPE_DIPPED, geokret=geokret)\
            .set_moved_on_datetime("2018-12-30T12:57:25")\
            .set_coordinates(52.07567, 9.35367)\
            .set_waypoint('ABC123')\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(0)

        MovePayload(MOVE_TYPE_DROPPED, geokret=geokret)\
            .set_moved_on_datetime("2018-12-30T12:57:33")\
            .set_coordinates(52.07567, 9.35367)\
            .set_waypoint('ABC123')\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(1)

        MovePayload(MOVE_TYPE_DROPPED, geokret=geokret2)\
            .set_moved_on_datetime("2018-12-30T12:57:45")\
            .set_coordinates(52.07567, 9.35367)\
            .set_waypoint('ABC123')\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(2)

        MovePayload(MOVE_TYPE_DIPPED, geokret=geokret2)\
            .set_moved_on_datetime("2018-12-30T12:57:49")\
            .set_coordinates(42.0, 42.0)\
            .set_waypoint('DEF456')\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(1)

    @request_context
    def test_search_by_coordinates(self):
        geokret = self.blend_geokret(created_on_datetime="2018-12-30T12:56:31")
        geokret2 = self.blend_geokret(created_on_datetime="2018-12-30T12:56:31")

        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(0)

        MovePayload(MOVE_TYPE_COMMENT, geokret=geokret)\
            .set_moved_on_datetime("2018-12-30T12:57:16")\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(0)

        MovePayload(MOVE_TYPE_DIPPED, geokret=geokret)\
            .set_moved_on_datetime("2018-12-30T12:57:25")\
            .set_coordinates(52.07567, 9.35367)\
            .set_waypoint('ABC123')\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(0)

        MovePayload(MOVE_TYPE_DROPPED, geokret=geokret)\
            .set_moved_on_datetime("2018-12-30T12:57:33")\
            .set_coordinates(52.07567, 9.35367)\
            .set_waypoint('ABC123')\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(1)

        MovePayload(MOVE_TYPE_DROPPED, geokret=geokret2)\
            .set_moved_on_datetime("2018-12-30T12:57:45")\
            .set_coordinates(52.07567, 9.35367)\
            .set_waypoint('ABC123')\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(2)

        MovePayload(MOVE_TYPE_DIPPED, geokret=geokret2)\
            .set_moved_on_datetime("2018-12-30T12:57:49")\
            .set_coordinates(42.0, 42.0)\
            .set_waypoint('DEF456')\
            .post(user=self.user_1)
        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(1)

    @request_context
    def test_hide_archived_geokrety(self):
        geokret = self.blend_geokret(created_on_datetime="2019-01-01T02:21:26")

        MovePayload(MOVE_TYPE_DROPPED, geokret=geokret)\
            .set_moved_on_datetime("2019-01-01T02:21:38")\
            .set_coordinates(52.07567, 9.35367)\
            .set_waypoint('ABC123')\
            .post(user=self.admin)
        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(1)
        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(1)

        move = MovePayload(MOVE_TYPE_ARCHIVED, geokret=geokret)\
            .set_moved_on_datetime("2019-01-01T02:21:46")\
            .post(user=self.admin)
        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(0)
        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(0)

        MovePayload(moved_on_datetime="2019-01-01T02:21:30")\
            .patch(move.id, user=self.admin)
        GeokretyInCachePayload()\
            .get_collection(args={'latitude': 52.07567, 'longitude': 9.35367})\
            .assertCount(1)
        GeokretyInCachePayload()\
            .get_collection(args={'waypoint': 'ABC123'})\
            .assertCount(1)
