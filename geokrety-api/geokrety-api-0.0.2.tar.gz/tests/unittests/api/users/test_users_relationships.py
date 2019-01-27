# -*- coding: utf-8 -*-

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.user import UserPayload


class TestUsersRelationships(BaseTestCase):
    """Test Users relationships"""

    @request_context
    def test_user_move_relationship(self):
        move = self.blend_move(author=self.user_1)
        UserPayload(_url_collection="/v1/users/{}/relationships/moves".format(self.user_1.id))\
            .get_collection()\
            .assertHasDatas('move', [move.id])

    @request_context
    def test_user_news_relationship(self):
        news = self.blend_news(author=self.user_1)
        UserPayload(_url_collection="/v1/users/{}/relationships/news".format(self.user_1.id))\
            .get_collection()\
            .assertHasDatas('news', [news.id])

    @request_context
    def test_user_news_comments_relationship(self):
        news_comment = self.blend_news_comment(author=self.user_1)
        UserPayload(_url_collection="/v1/users/{}/relationships/news-comments".format(self.user_1.id))\
            .get_collection()\
            .assertHasDatas('news-comment', [news_comment.id])

    @request_context
    def test_user_news_subscriptions_relationship(self):
        news_subscription = self.blend_news_subscription(user=self.user_1)
        UserPayload(_url_collection="/v1/users/{}/relationships/news-subscriptions".format(self.user_1.id))\
            .get_collection()\
            .assertHasDatas('news-subscription', [news_subscription.id])

    @request_context
    def test_user_geokrety_owned_relationship(self):
        geokret = self.blend_geokret(owner=self.user_1)
        UserPayload(_url_collection="/v1/users/{}/relationships/geokrety-owned".format(self.user_1.id))\
            .get_collection()\
            .assertHasDatas('geokret', [geokret.id])

    @request_context
    def test_user_geokrety_held_relationship(self):
        geokret = self.blend_geokret(holder=self.user_1)
        UserPayload(_url_collection="/v1/users/{}/relationships/geokrety-held".format(self.user_1.id))\
            .get_collection()\
            .assertHasDatas('geokret', [geokret.id])
