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
                                                     NO_HTML_TEST_CASES,
                                                     NO_HTML_TEST_CASES_SORT,
                                                     UTF8_TEST_CASES)


class TestMoveCreateCommon(BaseTestCase):
    """Test Move create Common"""

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_as_anonymous_is_forbidden(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .post(code=401)

    @request_context
    def test_bad_move_type(self):
        geokret = self.blend_geokret()
        MovePayload(666, geokret=geokret)\
            .set_coordinates()\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/type')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_type_is_mandatory(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_relationships('type')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/relationships/type')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_on_datetime_must_be_present(self, move_type):
        geokret = self.blend_geokret(created_on_datetime='2018-10-07T15:30:52')
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_attribute('moved-on-datetime')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_on_datetime_must_be_after_born_date(self, move_type):
        geokret = self.blend_geokret(created_on_datetime='2018-10-07T15:30:52')
        payload = MovePayload(move_type, geokret=geokret)\
            .set_coordinates()

        payload.set_moved_on_datetime(geokret.created_on_datetime)\
            .post(user=self.user_1)
        payload.set_moved_on_datetime('2018-10-07T19:00:00')\
            .post(user=self.user_1)
        payload.set_moved_on_datetime('2018-10-07T10:00:00')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_on_datetime_must_not_be_in_the_future(self, move_type):
        geokret = self.blend_geokret(created_on_datetime='2018-10-07T15:30:52')
        payload = MovePayload(move_type, geokret=geokret)\
            .set_coordinates()

        payload.set_moved_on_datetime(datetime.utcnow() - timedelta(hours=1))\
            .post(user=self.user_1)
        payload.set_moved_on_datetime(datetime.now() + timedelta(hours=6))\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED, 422],
        [MOVE_TYPE_GRABBED, 422],
        [MOVE_TYPE_COMMENT, 201],
        [MOVE_TYPE_SEEN, 422],
        [MOVE_TYPE_DIPPED, 422],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_move_on_datetime_must_not_be_at_the_same_datetime(self, move_type, expected):
        geokret = self.blend_geokret(created_on_datetime='2018-10-07T15:30:52')
        payload = MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_moved_on_datetime('2018-10-09T19:40:28')
        payload.post(user=self.user_1)
        move = payload.post(user=self.user_1, code=expected)
        if expected == 422:
            move.assertRaiseJsonApiError('/data/attributes/moved-on-datetime')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_username_is_not_overridable(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_username('Some unregistered user')\
            .post(user=self.user_1)\
            .assertHasAttribute('username', '')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_comment_may_be_absent(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_attribute('comment')\
            .post(user=self.user_1)\
            .assertHasAttribute('comment', '')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_comment(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_comment('Some text')\
            .post(user=self.user_1)\
            .assertHasAttribute('comment', 'Some text')

    @parameterized.expand(HTML_SUBSET_TEST_CASES)
    @request_context
    def test_field_comment_accept_html_subset(self, comment, expected):
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_GRABBED, geokret=geokret)\
            .set_comment(comment)\
            .post(user=self.user_1)\
            .assertHasAttribute('comment', expected)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_comment_accept_unicode(self, comment, expected):
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_GRABBED, geokret=geokret)\
            .set_comment(comment)\
            .post(user=self.user_1)\
            .assertHasAttribute('comment', expected)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_relationship_author_defaults_to_current_user(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_relationships('author')\
            .post(user=self.user_1)\
            .assertHasRelationshipAuthorData(self.user_1.id)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_relationship_author_is_not_overridable(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_author(self.user_2.id)\
            .post(user=self.user_1, code=403)\
            .assertRaiseJsonApiError('/data/relationships/author')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_relationship_author_can_be_overrided_by_an_admin(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_author(self.user_2.id)\
            .post(user=self.admin)\
            .assertHasRelationshipAuthorData(self.user_2.id)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_application_name_may_be_absent(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_attribute('application_name')\
            .post(user=self.user_1)\
            .assertHasAttribute('application-name', None)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_application_name_may_be_none(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_application_name(None)\
            .post(user=self.user_1)\
            .assertHasAttribute('application-name', None)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_application_name(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_application_name('Some name')\
            .post(user=self.user_1)\
            .assertHasAttribute('application-name', 'Some name')

    @parameterized.expand(NO_HTML_TEST_CASES)
    @request_context
    def test_field_application_name_no_html(self, application_name, expected):
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_DIPPED, geokret=geokret)\
            .set_coordinates()\
            .set_application_name(application_name)\
            .post(user=self.user_1)\
            .assertHasAttribute('application-name', expected)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_application_version_may_be_absent(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_attribute('application_version')\
            .post(user=self.user_1)\
            .assertHasAttribute('application-version', None)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_application_version_may_be_none(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_application_version(None)\
            .post(user=self.user_1)\
            .assertHasAttribute('application-version', None)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_application_version(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_application_version('1.0.0')\
            .post(user=self.user_1)\
            .assertHasAttribute('application-version', '1.0.0')

    @parameterized.expand(NO_HTML_TEST_CASES_SORT)
    @request_context
    def test_field_application_version_no_html(self, application_version, expected):
        geokret = self.blend_geokret()
        MovePayload(MOVE_TYPE_DIPPED, geokret=geokret)\
            .set_coordinates()\
            .set_application_version(application_version)\
            .post(user=self.user_1)\
            .assertHasAttribute('application-version', expected)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_application_version_too_long(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            .set_application_version('1.0.0.1.0.0.1.0.0.1.0.0.1.0.0')\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/attributes/application-version')

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_comment_count_is_computed_and_not_overridable(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._set_attribute('comments-count', 666)\
            .post(user=self.user_1)\
            .assertHasAttribute('comments-count', 0)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_picture_count_is_computed_and_not_overridable(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._set_attribute('pictures-count', 666)\
            .post(user=self.user_1)\
            .assertHasAttribute('pictures-count', 0)

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_creation_datetime_set_automatically(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_attribute('created-on-datetime')\
            .post(user=self.admin)\
            .assertCreationDateTime()

    @parameterized.expand([
        [MOVE_TYPE_DROPPED],
        [MOVE_TYPE_GRABBED],
        [MOVE_TYPE_COMMENT],
        [MOVE_TYPE_SEEN],
        [MOVE_TYPE_DIPPED],
    ], doc_func=custom_name_geokrety_move_type)
    @request_context
    def test_field_update_datetime_set_automatically(self, move_type):
        geokret = self.blend_geokret()
        MovePayload(move_type, geokret=geokret)\
            .set_coordinates()\
            ._del_attribute('updated-on-datetime')\
            .post(user=self.admin)\
            .assertUpdatedDateTime()
