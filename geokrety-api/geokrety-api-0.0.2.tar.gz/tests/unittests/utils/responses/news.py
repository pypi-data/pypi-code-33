# -*- coding: utf-8 -*-

from geokrety_api_models import User

from .base import BaseResponse
from .collections import BaseCollectionResponse


class NewsResponse(BaseResponse):

    def assertHasRelationshipAuthor(self):
        self.assertHasRelationshipSelf('author', '/v1/news/%s/relationships/author' % self.id)
        self.assertHasRelationshipRelated('author', '/v1/news/%s/author' % self.id)
        return self

    def assertHasRelationshipNewsComments(self):
        self.assertHasRelationshipSelf('comments', '/v1/news/%s/relationships/comments' % self.id)
        self.assertHasRelationshipRelated('comments', '/v1/news/%s/comments' % self.id)
        return self

    def assertHasRelationshipAuthorData(self, user):
        user_id = user.id if isinstance(user, User) else user
        self.assertHasRelationshipData('author', user_id, 'user')
        return self

    def assertHasPublicAttributes(self, obj):
        self.assertHasAttribute('title', obj.title)
        self.assertHasAttribute('content', obj.content)
        self.assertHasAttribute('username', obj.username)
        self.assertHasAttribute('comments-count', obj.comments_count)
        self.assertHasAttribute('last-comment-datetime', obj.last_comment_datetime)
        self.assertHasRelationshipAuthor()
        self.assertHasRelationshipNewsComments()
        return self


class NewsCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(NewsCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(NewsResponse(data_))
        self['data'] = datas
