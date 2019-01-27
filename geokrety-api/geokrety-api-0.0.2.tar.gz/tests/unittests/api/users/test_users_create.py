# -*- coding: utf-8 -*-

from decimal import Decimal

from parameterized import parameterized

from app.api.helpers.db import safe_query
from geokrety_api_models import User
from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.user import UserPayload
from tests.unittests.utils.static_test_cases import (NO_HTML_TEST_CASES,
                                                     UTF8_TEST_CASES)


class TestUserCreate(BaseTestCase):
    """Test User create"""

    @request_context
    def test_can_be_posted_as_anonymous(self):
        UserPayload()\
            .set_name('someone')\
            .set_email('someone@example.org')\
            .set_password('super secret passord')\
            .set_language('pl')\
            .set_country('pl')\
            .post(user=None)\
            .assertHasAttribute('country', 'pl')\
            .assertHasAttribute('language', 'pl')\
            .assertHasAttribute('name', 'someone')\
            .assertDateTimePresent('join-datetime')\


    @parameterized.expand([
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_can_be_posted_as(self, username):
        user = getattr(self, username) if username else None
        UserPayload()\
            .post(user=user, code=403)

    @parameterized.expand([
        ['name'],
        ['email'],
        ['password'],
    ])
    @request_context
    def test_mandatory_field(self, attribute):
        UserPayload().blend()\
            ._del_attribute(attribute)\
            .post(code=422)\
            .assertJsonApiErrorCount(1)\
            .assertRaiseJsonApiError('/data/attributes/{}'.format(attribute))

    @request_context
    def test_unicity_field_username(self):
        UserPayload().blend().set_name('someone').post()
        UserPayload().blend().set_name('someone').post(code=422)\
            .assertJsonApiErrorCount(1)\
            .assertRaiseJsonApiError('/data/attributes/name')

    @request_context
    def test_unicity_field_email(self):
        UserPayload().blend().set_email('someone@example.org').post()
        UserPayload().blend().set_email('someone@example.org').post(code=422)\
            .assertJsonApiErrorCount(1)\
            .assertRaiseJsonApiError('/data/attributes/email')

    @parameterized.expand([
        ['language'],
        ['country'],
        ['latitude'],
        ['longitude'],
        ['daily-mails'],
        ['observation-radius'],
        ['statpic-id'],
        ['hour'],
    ])
    @request_context
    def test_optionnal_fields(self, attribute):
        UserPayload().blend()\
            ._del_attribute(attribute)\
            .post()

    @request_context
    def test_backend_generate_secid(self):
        payload = UserPayload().blend()
        response = payload.post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertNotEqual(unicode(payload['data']['attributes']['secid']), user.secid)

    @request_context
    def test_backend_generate_join_date_time(self):
        response = UserPayload().blend()\
            ._del_attribute('join-datetime')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        user.join_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    @request_context
    def test_backend_generate_last_update_datetime(self):
        response = UserPayload().blend()\
            ._del_attribute('last-update-datetime')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        user.last_update_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    @request_context
    def test_backend_generate_last_mail_datetime(self):
        response = UserPayload().blend()\
            ._del_attribute('last-mail-datetime')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertIsNone(user.last_mail_datetime)

    @request_context
    def test_backend_generate_last_login_datetime(self):
        response = UserPayload().blend()\
            ._del_attribute('last-login-datetime')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertIsNone(user.last_login_datetime)

    @request_context
    def test_valid_email(self):
        response = UserPayload().blend()\
            .set_email("A@VALID.EMAIL")\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertEqual(user.email, "A@VALID.EMAIL")

    @request_context
    def test_invalid_email(self):
        UserPayload().blend()\
            .set_email("NOT_A_VALID_EMAIL")\
            .post(code=422)\
            .assertJsonApiErrorCount(1)\
            .assertRaiseJsonApiError('/data/attributes/email')

    @request_context
    def test_password_is_encrypted(self):
        import phpass
        phpass.PasswordHash.hash_password = self.hash_password_original
        payload = UserPayload().blend()
        response = payload.post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertNotEqual(user.password, payload['data']['attributes']['password'])
        self.assertEqual(user.password[:7], "$2a$11$")

    @request_context
    def test_languages_defaults_to_english_if_missing(self):
        UserPayload().blend()\
            ._del_attribute('language')\
            .post()\
            .assertHasAttribute('language', 'en')

    @request_context
    def test_languages_defaults_to_english_if_empty(self):
        UserPayload().blend()\
            .set_language('')\
            .post()\
            .assertHasAttribute('language', 'en')

    @parameterized.expand([
        ['en', 201],
        ['fr', 201],
        ['francais', 422],
        ['tt', 422],
        ['t', 422],
    ])
    @request_context
    def test_languages_are_checked_against_static_list(self, language, expected):
        response = UserPayload().blend()\
            .set_language(language)\
            .post(code=expected)
        if expected == 422:
            response.assertRaiseJsonApiError('/data/attributes/language')
        else:
            response.assertHasAttribute('language', language)

    @parameterized.expand([
        ['fr', 201],
        ['pl', 201],
        ['de', 201],
        ['uk', 201],
        ['ru', 201],
        ['ro', 201],
        ['zz', 422],
    ])
    @request_context
    def test_countries_are_checked_against_static_list(self, country, expected):
        response = UserPayload().blend()\
            .set_country(country)\
            .post(code=expected)
        if expected == 422:
            response.assertRaiseJsonApiError('/data/attributes/country')
        else:
            response.assertHasAttribute('country', country)

    @request_context
    def test_countries_defaults_to_none_if_missing(self):
        UserPayload().blend()\
            ._del_attribute('country')\
            .post()\
            .assertHasAttribute('country', None)

    @request_context
    def test_countries_defaults_to_none_if_empty(self):
        UserPayload().blend()\
            .set_country('')\
            .post()\
            .assertHasAttribute('country', None)

    @parameterized.expand([
        ['', 422],
        ['abc.def', 422],
        [u'0', 201],
        ['0', 201],
        ['0.0', 201],
        ['1', 201],
        ['1.0', 201],
        [0, 201],
        [0.0, 201],
        [1, 201],
        [1.0, 201],
        [-180.0, 422],
        [-91.0, 422],
        [-90.1, 422],
        [-90.001, 422],
        [90.001, 422],
        [90.1, 422],
        [91.0, 422],
        [180.0, 422],
    ])
    @request_context
    def test_home_latitude_as_decimal_degrees(self, latitude, expected):
        response = UserPayload().blend()\
            .set_latitude(latitude)\
            .post(code=expected)
        if expected == 422:
            response.assertRaiseJsonApiError('/data/attributes/latitude')
        else:
            user = safe_query(self, User, 'id', response.id, 'id')
            self.assertEqual(user.latitude, Decimal(latitude))

    @parameterized.expand([
        ['', 422],
        [' ', 422],
        ['abc.def', 422],
        [u'0', 201],
        ['0', 201],
        ['0.0', 201],
        ['1', 201],
        ['1.0', 201],
        [0, 201],
        [0.0, 201],
        [1, 201],
        [1.0, 201],
        [-250.0, 422],
        [-181.0, 422],
        [-180.1, 422],
        [-180.001, 422],
        [180.001, 422],
        [180.1, 422],
        [181.0, 422],
        [250.0, 422],
    ])
    @request_context
    def test_home_longitude_as_decimal_degrees(self, longitude, expected):
        response = UserPayload().blend()\
            .set_longitude(longitude)\
            .post(code=expected)
        if expected == 422:
            response.assertRaiseJsonApiError('/data/attributes/longitude')
        else:
            user = safe_query(self, User, 'id', response.id, 'id')
            self.assertEqual(user.longitude, Decimal(longitude))

    @request_context
    def test_home_latitude_default_to_null_if_none(self):
        response = UserPayload().blend()\
            .set_latitude(None)\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertIsNone(user.latitude)

    @request_context
    def test_home_latitude_default_to_null_if_missing(self):
        response = UserPayload().blend()\
            ._del_attribute('latitude')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertIsNone(user.latitude)

    @request_context
    def test_home_longitude_default_to_null_if_none(self):
        response = UserPayload().blend()\
            .set_longitude(None)\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertIsNone(user.longitude)

    @request_context
    def test_home_longitude_default_to_null_if_missing(self):
        response = UserPayload().blend()\
            ._del_attribute('longitude')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertIsNone(user.longitude)

    @parameterized.expand([
        [None, 201],
        ['', 422],
        [' ', 422],
        ['a', 422],
        ['0', 201],
        ['0.0', 422],
        [0, 201],
        [0.0, 201],
        [1, 201, True],
        [1.0, 201, True],
        [1.1, 422],
    ])
    @request_context
    def test_field_daily_mails_is_boolean(self, value, expected_code, expected=False):
        response = UserPayload().blend()\
            .set_daily_mails(value)\
            .post(code=expected_code)
        if expected_code == 422:
            response.assertRaiseJsonApiError('/data/attributes/daily-mails')
        else:
            user = safe_query(self, User, 'id', response.id, 'id')
            self.assertEqual(user.daily_mails, expected)

    @request_context
    def test_field_daily_mails_default_to_false_if_missing(self):
        response = UserPayload().blend()\
            ._del_attribute('daily-mails')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertFalse(user.daily_mails)

    @parameterized.expand([
        ['', 422],
        [' ', 422],
        ['a', 422],
        ['0', 201],
        ['0.0', 422],
        [0, 201],
        [0.0, 201],
        [1, 201],
        [1.0, 201],
        [1.1, 201],
    ])
    @request_context
    def test_field_observation_radius_is_integer(self, radius, expected):
        response = UserPayload().blend()\
            .set_observation_radius(radius)\
            .post(code=expected)
        if expected == 422:
            response.assertRaiseJsonApiError('/data/attributes/observation-radius')
        else:
            user = safe_query(self, User, 'id', response.id, 'id')
            self.assertEqual(user.observation_radius, int(radius))

    @request_context
    def test_field_observation_radius_default_to_zero_if_none(self):
        response = UserPayload().blend()\
            .set_observation_radius(None)\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertEqual(user.observation_radius, 0)

    @request_context
    def test_field_observation_radius_default_to_zero_if_missing(self):
        response = UserPayload().blend()\
            ._del_attribute('observation-radius')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertEqual(user.observation_radius, 0)

    @parameterized.expand([
        [-1, 422],
        [0, 201],
        [1, 201],
        [2, 201],
        [8, 201],
        [9, 201],
        [10, 201],
        [11, 422],
        [666, 422],
    ])
    @request_context
    def test_field_observation_radius_is_betwwen_zero_ten(self, radius, expected):
        response = UserPayload().blend()\
            .set_observation_radius(radius)\
            .post(code=expected)
        if expected == 422:
            response.assertRaiseJsonApiError('/data/attributes/observation-radius')
        else:
            user = safe_query(self, User, 'id', response.id, 'id')
            self.assertEqual(user.observation_radius, int(radius))

    @parameterized.expand([
        ['', 422],
        [' ', 422],
        ['a', 422],
        ['0', 201],
        ['0.0', 422],
        [0.0, 201],
        [1.0, 201],
        [1.1, 201],
        [-1, 422],
        [0, 201],
        [1, 201],
        [2, 201],
        [8, 201],
        [9, 201],
        [10, 201],
        [11, 201],
        [21, 201],
        [22, 201],
        [23, 201],
        [24, 422],
        [666, 422],
    ])
    @request_context
    def test_field_hour_is_integer(self, hour, expected):
        response = UserPayload().blend()\
            .set_hour(hour)\
            .post(code=expected)
        if expected == 422:
            response.assertRaiseJsonApiError('/data/attributes/hour')
        else:
            user = safe_query(self, User, 'id', response.id, 'id')
            self.assertEqual(user.hour, int(hour))

    @request_context
    def test_field_hour_default_to_random_if_none(self):
        response = UserPayload().blend()\
            .set_hour(None)\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertGreaterEqual(user.hour, 0)
        self.assertLessEqual(user.hour, 23)

    @request_context
    def test_field_hour_default_to_random_if_missing(self):
        response = UserPayload().blend()\
            ._del_attribute('hour')\
            .post()
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertGreaterEqual(user.hour, 0)
        self.assertLessEqual(user.hour, 23)

    @parameterized.expand(UTF8_TEST_CASES)
    @request_context
    def test_field_username_support_utf8(self, username, expected):
        response = UserPayload().blend()\
            .set_name(username)\
            .post()\
            .assertHasAttribute('name', expected)
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertEqual(user.name, expected)

    @parameterized.expand(NO_HTML_TEST_CASES)
    @request_context
    def test_field_username_cannot_be_blank(self, username, expected):
        response = UserPayload().blend()\
            .set_name(username)\
            .post()\
            .assertHasAttribute('name', expected)
        user = safe_query(self, User, 'id', response.id, 'id')
        self.assertEqual(user.name, expected)
