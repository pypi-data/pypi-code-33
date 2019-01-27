# -*- coding: utf-8 -*-

from parameterized import parameterized

from app.api.helpers.data_layers import (GEOKRET_TYPE_BOOK, GEOKRET_TYPE_COIN,
                                         GEOKRET_TYPE_HUMAN,
                                         GEOKRET_TYPE_KRETYPOST,
                                         GEOKRET_TYPE_TRADITIONAL,
                                         MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_move_type,
                                                  custom_name_geokrety_type,
                                                  request_context)
from tests.unittests.utils.payload.geokret import GeokretPayload
from tests.unittests.utils.static_test_cases import (EMPTY_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES,
                                                     NO_HTML_TEST_CASES,
                                                     UTF8_TEST_CASES)


class TestGeokretyEdit(BaseTestCase):
    """Test edit Geokrety"""

    @request_context
    def test_as_anonymous(self):
        geokret = self.blend_geokret()
        GeokretPayload().patch(geokret.id, user=None, code=401)

    @request_context
    def test_as_owner(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .patch(geokret.id, user=self.user_1)

    @request_context
    def test_as_someone(self):
        geokret = self.blend_geokret()
        GeokretPayload()\
            .patch(geokret.id, user=self.user_1, code=403)

    @request_context
    def test_as_admin(self):
        geokret = self.blend_geokret()
        GeokretPayload()\
            .patch(geokret.id, user=self.admin)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_ARCHIVED],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_cannot_edit_even_when_user_has_touched(self, move_type):
        geokret = self.blend_geokret(created_on_datetime="2018-09-22T18:18:55")
        self.blend_move(geokret=geokret, author=self.user_1,
                        type=move_type,
                        moved_on_datetime="2018-09-22T18:18:56")
        self.blend_move(geokret=geokret, author=self.user_2,
                        type=MOVE_TYPE_GRABBED,
                        moved_on_datetime="2018-09-22T18:18:57")
        GeokretPayload("New name")\
            .patch(geokret.id, user=self.user_1, code=403)

    @request_context
    def test_field_name(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload("New name")\
            .patch(geokret.id, user=self.user_1)\
            .assertHasAttribute('name', "New name")

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_name_cannot_be_blank(self, name):
        geokret = self.blend_geokret()
        GeokretPayload("New name")\
            .set_name(name)\
            .patch(geokret.id, user=self.admin, code=422)\
            .assertRaiseJsonApiError('/data/attributes/name')

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_name_accept_unicode(self, name, result):
        geokret = self.blend_geokret()
        GeokretPayload("New name")\
            .set_name(name)\
            .patch(geokret.id, user=self.admin)\
            .assertHasAttribute('name', result)

    @parameterized.expand(NO_HTML_TEST_CASES)
    @request_context
    def test_field_name_doesnt_accept_html(self, name, result):
        geokret = self.blend_geokret()
        GeokretPayload("New name")\
            .set_name(name)\
            .patch(geokret.id, user=self.admin)\
            .assertHasAttribute('name', result)

    @request_context
    def test_field_description(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .set_description("New description")\
            .patch(geokret.id, user=self.user_1)\
            .assertHasAttribute('description', "New description")

    @parameterized.expand([
        [None, ''],
        ['', ''],
        [' ', ''],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_description_can_be_blank(self, description, expect):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .set_description(description)\
            .patch(geokret.id, user=self.user_1)\
            .assertHasAttribute('description', expect)

    @parameterized.expand(HTML_SUBSET_TEST_CASES)
    @request_context
    def test_field_description_accept_html_subset(self, description, result):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .set_description(description)\
            .patch(geokret.id, user=self.user_1)\
            .assertHasAttribute('description', result)

    @parameterized.expand([
        ['admin', GEOKRET_TYPE_COIN, True],
        ['admin', GEOKRET_TYPE_TRADITIONAL, True],
        ['admin', GEOKRET_TYPE_BOOK, True],
        ['admin', GEOKRET_TYPE_HUMAN, True],
        ['admin', GEOKRET_TYPE_COIN, True],
        ['admin', GEOKRET_TYPE_KRETYPOST, True],
        ['admin', "non-existent", False],
        ['user_1', GEOKRET_TYPE_COIN, True],
        ['user_1', GEOKRET_TYPE_TRADITIONAL, True],
        ['user_1', GEOKRET_TYPE_BOOK, True],
        ['user_1', GEOKRET_TYPE_HUMAN, True],
        ['user_1', GEOKRET_TYPE_COIN, True],
        ['user_1', GEOKRET_TYPE_KRETYPOST, True],
        ['user_1', "non-existent", False],
    ], doc_func=custom_name_geokrety_type)
    @request_context
    def test_field_type_can_be_changed(self, username, geokret_type, expected):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_1, type=GEOKRET_TYPE_TRADITIONAL)
        payload = GeokretPayload().set_geokret_type(geokret_type)
        if expected:
            payload.patch(geokret.id, user=user)\
                .assertHasRelationshipGeokretyTypeData(geokret_type)
        else:
            payload.patch(geokret.id, user=user, code=422)\
                .assertRaiseJsonApiError('/data/relationships/type')

    @request_context
    def test_some_fields_are_not_overridable(self):
        geokret = self.blend_geokret(
            owner=self.user_1,
            missing=False,
            distance=12,
            caches_count=12,
            pictures_count=12,
            created_on_datetime="2018-09-22T19:34:41",
            updated_on_datetime="2018-09-22T19:34:42",
        )
        GeokretPayload()\
            ._set_attribute('missing', True)\
            ._set_attribute('distance', 1000)\
            ._set_attribute('caches-count', 1000)\
            ._set_attribute('pictures-count', 1000)\
            ._set_attribute('average-rating', 1000)\
            ._set_attribute('created-on-datetime', "2018-09-22T19:38:28")\
            ._set_attribute('updated-on-datetime', "2018-09-22T19:38:29")\
            .patch(geokret.id, user=self.user_1)\
            .assertHasAttribute('missing', False)\
            .assertHasAttribute('distance', 12)\
            .assertHasAttribute('caches-count', 12)\
            .assertHasAttribute('pictures-count', 12)\
            .assertHasAttribute('average-rating', 0.0)\
            .assertHasAttributeDateTime('created-on-datetime', "2018-09-22T19:34:41")\
            .assertHasAttributeDateTime('updated-on-datetime', geokret.updated_on_datetime)

    @request_context
    def test_field_updated_on_datetime_automatically_changed(self):
        geokret = self.blend_geokret(owner=self.user_1, created_on_datetime="2018-09-22T20:27:08")
        updated_on_datetime = geokret.updated_on_datetime
        GeokretPayload()\
            .patch(geokret.id, user=self.user_1)\
            .assertNotHasAttribute('updated-on-datetime', updated_on_datetime.strftime("%Y-%m-%dT%H:%M:%S"))\
            .assertHasAttributeDateTime('updated-on-datetime', geokret.updated_on_datetime)

    @request_context
    def test_relationships_owner_can_be_overrided_as_admin(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .set_owner(self.user_2)\
            .patch(geokret.id, user=self.admin)\
            .assertHasRelationshipOwnerData(self.user_2.id)

    @request_context
    def test_relationships_owner_overrided_ignored_as_owner(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .set_owner(self.user_2)\
            .patch(geokret.id, user=self.user_1)\
            .assertHasRelationshipOwnerData(self.user_1.id)

    @request_context
    def test_relationships_owner_override_forbidden_as_authenticated(self):
        geokret = self.blend_geokret(owner=self.user_1)
        GeokretPayload()\
            .set_owner(self.user_2)\
            .patch(geokret.id, user=self.user_2, code=403)

    @parameterized.expand([
        ['admin'],
        ['user_1'],  # Owner
    ])
    @request_context
    def test_relationships_holder_override_is_ignored_as(self, username):
        user = getattr(self, username) if username else None
        geokret = self.blend_geokret(owner=self.user_1, holder=self.user_1)
        GeokretPayload()\
            .set_holder(self.user_2)\
            .patch(geokret.id, user=user)\
            .assertHasRelationshipOwnerData(self.user_1.id)

    @parameterized.expand([
        ['admin'],
        ['user_1'],  # Owner
    ])
    @request_context
    def test_relationships_moves_cannot_be_forced_as(self, username):
        user = getattr(self, username) if username else None
        geokret_1 = self.blend_geokret(owner=self.user_1, holder=self.user_1)
        geokret_2 = self.blend_geokret()

        moves = self.blend_move(geokret=geokret_2, count=2)
        moves_ids = [move.id for move in moves]

        GeokretPayload()\
            ._set_relationships_many('moves', 'move', moves_ids)\
            .patch(geokret_1.id, user=user, args={'include': 'moves'})\
            .assertHasRelationshipMovesDatas([])
