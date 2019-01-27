# -*- coding: utf-8 -*-

from flask_rest_jsonapi.exceptions import ObjectNotFound
from parameterized import parameterized

from app.api.helpers.data_layers import (GEOKRET_TYPE_BOOK, GEOKRET_TYPE_COIN,
                                         GEOKRET_TYPE_HUMAN,
                                         GEOKRET_TYPE_KRETYPOST,
                                         GEOKRET_TYPE_TRADITIONAL,
                                         MOVE_TYPE_DIPPED)
from app.api.helpers.db import safe_query
from geokrety_api_models import Move
from tests.unittests.utils.base_test_case import (BaseTestCase,
                                                  custom_name_geokrety_type_basic,
                                                  request_context)
from tests.unittests.utils.payload.geokret import GeokretPayload
from tests.unittests.utils.payload.move import MovePayload
from tests.unittests.utils.static_test_cases import (EMPTY_TEST_CASES,
                                                     HTML_SUBSET_TEST_CASES,
                                                     NO_HTML_TEST_CASES,
                                                     UTF8_TEST_CASES)


class TestGeokretCreate(BaseTestCase):
    """Test GeoKrety creation"""

    @request_context
    def test_as_anonymous_user(self):
        GeokretPayload().post(user=None, code=401)

    @request_context
    def test_as_authenticated_user(self):
        GeokretPayload("Name").post(user=self.user_1)

    @request_context
    def test_field_creation_datetime_is_auto_managed(self):
        GeokretPayload("Name")\
            .post(user=self.user_1)\
            .assertCreationDateTime()

    @request_context
    def test_field_update_datetime_is_auto_managed(self):
        GeokretPayload("Name")\
            .post(user=self.user_1)\
            .assertUpdatedDateTime()

    @request_context
    def test_field_creation_datetime_is_equal_to_update_datetime(self):
        GeokretPayload("Name")\
            .post(user=self.user_1)\
            .assertDateTimeAlmostEqual('created_on_datetime',
                                       'updated_on_datetime')

    @request_context
    def test_owner_is_the_connected_user_if_undefined(self):
        GeokretPayload("Name")\
            .post(user=self.user_1)\
            .assertHasRelationshipOwnerData(self.user_1.id)

    @request_context
    def test_owner_is_the_connected_user_if_undefined_even_for_admin(self):
        GeokretPayload("Name")\
            .post(user=self.admin)\
            .assertHasRelationshipOwnerData(self.admin.id)

    @request_context
    def test_owner_enforced_to_current_user(self):
        GeokretPayload("Name")\
            .set_owner(self.user_2)\
            .post(user=self.user_1)\
            .assertHasRelationshipOwnerData(self.user_1.id)

    @request_context
    def test_owner_enforced_by_admin(self):
        GeokretPayload("Name")\
            .set_owner(self.user_1)\
            .post(user=self.admin)\
            .assertHasRelationshipOwnerData(self.user_1.id)

    @parameterized.expand([
        [GEOKRET_TYPE_TRADITIONAL],
        [GEOKRET_TYPE_BOOK],
        [GEOKRET_TYPE_HUMAN],
        [GEOKRET_TYPE_COIN],
        [GEOKRET_TYPE_KRETYPOST],
    ], doc_func=custom_name_geokrety_type_basic)
    @request_context
    def test_geokrety_type_relationships_exists(self, geokret_type):
        GeokretPayload("Name")\
            .set_geokret_type(geokret_type)\
            .post(user=self.user_1)\
            .assertHasRelationshipGeokretyType()

    @parameterized.expand([
        [666],
        ["A"],
        ["777"],
        [u"yjgdf"],
        [u"ginieḰ"],
        [u""],
    ])
    @request_context
    def test_geokrety_type_non_existent(self, geokret_type):
        GeokretPayload("Name")\
            .set_geokret_type(geokret_type)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/relationships/type')

    @request_context
    def test_geokrety_type_missing(self):
        GeokretPayload("Name")\
            ._del_relationships('type')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/relationships/type')

    @request_context
    def test_field_name_must_be_present(self):
        GeokretPayload()\
            ._del_attribute('name')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/name')

    @parameterized.expand(EMPTY_TEST_CASES)
    @request_context
    def test_field_name_cannot_be_blank(self, name):
        GeokretPayload()\
            .set_name(name)\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/name')

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_name_accept_unicode(self, name, result):
        GeokretPayload()\
            .set_name(name)\
            .post(user=self.user_1)\
            .assertHasAttribute('name', result)

    @parameterized.expand(NO_HTML_TEST_CASES)
    @request_context
    def test_field_name_doesnt_accept_html(self, name, result):
        GeokretPayload()\
            .set_name(name)\
            .post(user=self.user_1)\
            .assertHasAttribute('name', result)

    @request_context
    def test_field_description_may_be_absent(self):
        GeokretPayload("Name")\
            ._del_attribute('description')\
            .post(user=self.user_1)\
            .assertHasAttribute('description', '')

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_description_accept_unicode(self, description, result):
        GeokretPayload("Name")\
            .set_description(description)\
            .post(user=self.user_1)\
            .assertHasAttribute('description', result)

    @parameterized.expand(HTML_SUBSET_TEST_CASES)
    @request_context
    def test_field_description_accept_html_subset(self, description, result):
        GeokretPayload("Name")\
            .set_description(description)\
            .post(user=self.user_1)\
            .assertHasAttribute('description', result)

    @parameterized.expand([
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_holder_defaults_to_current_user(self, username):
        user = getattr(self, username) if username else None
        GeokretPayload("Name")\
            .post(user=user)\
            .assertHasRelationshipHolderData(user.id)

    @request_context
    def test_holder_may_be_overrided_by_admin(self):
        GeokretPayload("Name")\
            .set_owner(self.user_1)\
            .post(user=self.admin)\
            .assertHasRelationshipHolderData(self.user_1.id)

    @request_context
    def test_geokret_may_be_born_at_home_but_user_has_no_home_coordinates(self):
        self.assertIsNone(self.user_1.latitude)
        self.assertIsNone(self.user_1.longitude)
        response = GeokretPayload("Name")\
            .post(user=self.user_1)

        with self.assertRaises(ObjectNotFound):
            safe_query(self, Move, 'geokret_id', response.id, 'geokret_id')

    @request_context
    def test_geokret_may_be_born_at_home_with_home_coordinates(self):
        user = self.blend_user(latitude=48.8566, longitude=2.3522)
        response = GeokretPayload("Name")\
            .set_born_at_home(True)\
            .post(user=user)
        MovePayload()\
            .get(response._get_relationships('last_move')['data']['id'])\
            .assertHasRelationshipMoveTypeData(MOVE_TYPE_DIPPED)\
            .assertHasAttribute('latitude', float(user.latitude))\
            .assertHasAttribute('longitude', float(user.longitude))\
            .assertHasAttributeDateTime('moved-on-datetime', response.created_on_datetime)\
            .assertHasRelationshipAuthorData(user)\
            .assertHasRelationshipGeokretData(response.id)\
            .assertHasAttribute('comment', "Born here")

    @request_context
    def test_bulk_operation_is_not_yet_supported(self):
        payload = GeokretPayload("Name")
        payload['data'] = [payload['data']]
        payload.post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data')
