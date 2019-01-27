# -*- coding: utf-8 -*-

from parameterized import parameterized

from tests.unittests.utils.base_test_case import BaseTestCase, request_context
from tests.unittests.utils.payload.news import NewsPayload


class TestNewsDetails(BaseTestCase):
    """Test News details"""

    @parameterized.expand([
        [None],
        ['admin'],
        ['user_1'],  # Owner
        ['user_2'],
    ])
    @request_context
    def test_news_details_has_normal_attributes_as(self, username):
        user = getattr(self, username) if username else None
        news = self.blend_news(author=self.user_1)
        NewsPayload().get(news.id, user=user)\
            .assertHasPublicAttributes(news)
