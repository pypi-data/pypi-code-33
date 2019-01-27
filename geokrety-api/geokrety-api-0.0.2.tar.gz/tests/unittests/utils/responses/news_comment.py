# -*- coding: utf-8 -*-

from geokrety_api_models import User

from .base import BaseResponse
from .collections import BaseCollectionResponse


class NewsCommentResponse(BaseResponse):

    def assertHasComment(self, value):
        self.assertHasAttribute('comment', value)
        return self

    def assertHasRelationshipAuthor(self):
        self.assertHasRelationshipSelf('author', '/v1/news-comments/%s/relationships/author' % self.id)
        self.assertHasRelationshipRelated('author', '/v1/news-comments/%s/author' % self.id)
        return self

    def assertHasRelationshipNews(self):
        self.assertHasRelationshipSelf('news', '/v1/news-comments/%s/relationships/news' % self.id)
        self.assertHasRelationshipRelated('news', '/v1/news-comments/%s/news' % self.id)
        return self

    def assertHasRelationshipAuthorData(self, user):
        user_id = user.id if isinstance(user, User) else user
        self.assertHasRelationshipData('author', user_id, 'user')
        return self

    def assertHasPublicAttributes(self, obj):
        self.assertHasAttribute('comment', obj.comment)
        self.assertHasAttribute('icon', obj.icon)
        self.assertCreationDateTime()
        self.assertHasRelationshipAuthor()
        self.assertHasRelationshipAuthorData(obj.author.id)
        self.assertHasRelationshipNews()
        return self


class NewsCommentCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(NewsCommentCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(NewsCommentResponse(data_))
        self['data'] = datas
