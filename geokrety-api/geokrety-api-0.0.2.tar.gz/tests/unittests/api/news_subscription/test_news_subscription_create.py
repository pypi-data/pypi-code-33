# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news_subscription import \
    NewsSubscriptionPayload


class TestNewsSubscriptionCreate(BaseTestCase):
    """Test NewsSubscription create"""

    @request_context
    def test_anonymous_cannot_subscribe(self):
        NewsSubscriptionPayload()\
            .post(user=None, code=401)

    @request_context
    def test_authenticated_can_subscribe(self):
        news = self.blend_news()
        NewsSubscriptionPayload(news=news)\
            .set_user(self.user_1)\
            .post(user=self.user_1)\
            .assertHasRelationshipUserData(self.user_1)\
            .assertHasRelationshipNewsData(news)

    @request_context
    def test_field_news_is_mandatory(self):
        NewsSubscriptionPayload()\
            .post(user=self.user_1, code=422)\
            .assertRaiseJsonApiError('/data/relationships/news')

    @parameterized.expand([
        ['admin'],
        ['user_1'],
        ['user_2'],
    ])
    @request_context
    def test_field_user_is_current_user_by_default(self, username):
        user = getattr(self, username) if username else None
        news = self.blend_news()
        NewsSubscriptionPayload(news=news)\
            .post(user=user, args={'include': 'user'})\
            .assertHasRelationshipUserData(user)

    @request_context
    def test_field_subscribed_on_datetime_cannot_be_overrided(self):
        news = self.blend_news()
        NewsSubscriptionPayload(news=news)\
            ._set_attribute('subscribed-on-datetime', "2018-09-24T23:57:37")\
            .post(user=self.user_1)\
            .assertDateTimePresent('subscribed-on-datetime')\
            .assertNotHasAttribute('subscribed-on-datetime', "2018-09-24T23:57:37")

    @request_context
    def test_authenticated_cannot_subscribe_someone_else(self):
        news = self.blend_news()
        NewsSubscriptionPayload(news=news)\
            .set_user(self.user_2)\
            .post(user=self.user_1, code=403)\
            .assertRaiseJsonApiError('/data/relationships/user')

    @request_context
    def test_admin_can_subscribe_someone_else(self):
        news = self.blend_news()
        NewsSubscriptionPayload(news=news)\
            .set_user(self.user_2)\
            .post(user=self.admin)\
            .assertHasRelationshipUserData(self.user_2)

    @request_context
    def test_unknown_news_raise_error(self):
        NewsSubscriptionPayload()\
            .set_news(666)\
            .post(user=self.admin, code=404)

    @request_context
    def test_unknown_user_raise_error(self):
        news = self.blend_news()
        NewsSubscriptionPayload(news=news)\
            .set_user(666)\
            .post(user=self.admin, code=404)
