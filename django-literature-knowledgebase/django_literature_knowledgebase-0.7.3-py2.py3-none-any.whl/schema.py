from graphene import Node, String
from graphene_django import DjangoObjectType

from . import choices, models


class ArticleNode(DjangoObjectType):

    source = String()
    article_url = String()
    fetch_url = String()
    summary_url = String()

    class Meta:
        model = models.Article
        interfaces = (Node, )

    def resolve_type(self, info):
        return choices.SOURCES[self.type]

    def article_url(self, info):
        return self.article_url

    def fetch_url(self, info):
        return self.fetch_url

    def summary_url(self, info):
        return self.summary_url
