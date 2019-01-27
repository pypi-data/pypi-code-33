# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import (MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_move_type,
                                                  request_context)
from tests.unittests.utils.payload.geokret import GeokretPayload


class TestGeokretyCollection(BaseTestCase):
    """Test GeoKrety collection"""

    @request_context
    def test_get_as_anonymous(self):
        geokrety = self.blend_geokret(owner=self.user_1, count=5)
        response = GeokretPayload()\
            .get_collection()\
            .assertCount(5)
        i = 0
        for geokret_response in response.data:
            geokret_response.assertHasPublicAttributes(geokrety[i])
            geokret_response.assertHasTrackingCode(None)
            i = i + 1

    @request_context
    def test_as_administrator(self):
        geokrety = self.blend_geokret(owner=self.user_1, count=5)
        response = GeokretPayload()\
            .get_collection(user=self.admin)\
            .assertCount(5)
        i = 0
        for geokret_response in response.data:
            geokret_response.assertHasPublicAttributes(geokrety[i])
            geokret_response.assertHasTrackingCode(geokrety[i].tracking_code)
            i = i + 1

    @request_context
    def test_as_authenticated(self):
        geokrety = self.blend_geokret(owner=self.user_1, count=5)
        response = GeokretPayload()\
            .get_collection(user=self.user_2)\
            .assertCount(5)
        i = 0
        for geokret_response in response.data:
            geokret_response.assertHasPublicAttributes(geokrety[i])
            geokret_response.assertHasTrackingCode(None)
            i = i + 1

    @request_context
    def test_as_owner(self):
        geokret = self.blend_geokret(owner=self.user_2)
        geokrety = self.blend_geokret(owner=self.user_1, count=4)
        response = GeokretPayload()\
            .get_collection(user=self.user_2)\
            .assertCount(5)
        response.data[0].assertHasPublicAttributes(geokret)
        response.data[0].assertHasTrackingCode(geokret.tracking_code)
        for i in range(1, 5):
            response.data[i].assertHasPublicAttributes(geokrety[i - 1])
            response.data[i].assertHasTrackingCode(None)

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
        geokret = self.blend_geokret(created_on_datetime="2018-09-20T23:15:30")
        self.blend_move(geokret=geokret, author=self.user_1, type=move_type,
                        moved_on_datetime="2018-09-20T23:15:31")
        self.blend_move(geokret=geokret, author=self.user_2, type=MOVE_TYPE_GRABBED,
                        moved_on_datetime="2018-09-20T23:15:32")
        response = GeokretPayload()\
            .get_collection(user=self.user_1)\
            .assertCount(1)

        if expected:
            response.data[0].assertHasTrackingCode(geokret.tracking_code)
        else:
            response.data[0].assertHasTrackingCode(None)

    @parameterized.expand([
        [None, False],
        ['admin', True],
        ['user_1', True],  # Owner
        ['user_2', False],
    ])
    @request_context
    def test_filter_by_tracking_code_as(self, username, expected):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_1)
        response = GeokretPayload()\
            .get_collection(user=user,
                            args={'filter': '[{"name":"tracking_code","op":"eq","val":"%s"}]' % (
                                geokret.tracking_code)})\
            .assertCount(1)

        if expected:
            response.data[0].assertHasTrackingCode(geokret.tracking_code)
        else:
            response.data[0].assertHasTrackingCode(None)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, True],
        [MOVE_TYPE_GRABBED, True],
        [MOVE_TYPE_COMMENT, False],
        [MOVE_TYPE_SEEN, True],
        [MOVE_TYPE_ARCHIVED, True],
        [MOVE_TYPE_DIPPED, True],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_filter_by_tracking_code_when_user_has_touched(self, move_type, expected):
        geokret = self.blend_geokret(author=self.user_2, created_on_datetime="2018-09-21T23:55:20")
        self.blend_move(geokret=geokret, author=self.user_1, type=move_type,
                        moved_on_datetime="2018-09-21T23:55:21")
        self.blend_move(geokret=geokret, author=self.user_2, type=MOVE_TYPE_GRABBED,
                        moved_on_datetime="2018-09-21T23:55:22")
        response = GeokretPayload()\
            .get_collection(user=self.user_1,
                            args={'filter': '[{"name":"tracking_code","op":"eq","val":"%s"}]' % (
                                geokret.tracking_code)})\
            .assertCount(1)

        if expected:
            response.data[0].assertHasTrackingCode(geokret.tracking_code)
        else:
            response.data[0].assertHasTrackingCode(None)
