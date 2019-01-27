# -*- coding: utf-8 -*-

from geokrety_api_models import User

from .base import BaseResponse
from .collections import BaseCollectionResponse


class BadgeResponse(BaseResponse):

    @property
    def filename(self):
        return self.get_attribute('filename')

    @property
    def upload_url(self):
        return self.get_attribute('upload_url')

    def assertHasName(self, value):
        self.assertHasAttribute('name', value)
        return self

    def assertHasDescription(self, value):
        self.assertHasAttribute('description', value)
        return self

    def assertHasFilename(self, value):
        self.assertHasAttribute('filename', value)
        return self

    def assertHasRelationshipAuthor(self):
        self.assertHasRelationshipSelf('author', '/v1/badges/%s/relationships/author' % self.id)
        self.assertHasRelationshipRelated('author', '/v1/badges/%s/author' % self.id)
        return self

    def assertHasRelationshipAuthorData(self, user):
        user_id = user.id if isinstance(user, User) else user
        self.assertHasRelationshipData('author', user_id, 'user')
        return self

    # def assertHasRelationshipHolders(self):
    #     self.assertHasRelationshipSelf('holders', '/v1/badges/%s/relationships/holders' % self.id)
    #     self.assertHasRelationshipRelated('holders', '/v1/badges/%s/holders' % self.id)
    #     return self
    #
    # def assertHasRelationshipHoldersData(self, user):
    #     user_id = user.id if isinstance(user, User) else user
    #     self.assertHasRelationshipData('holders', user_id, 'user')
    #     return self

    def assertHasPublicAttributes(self, obj):
        self.assertHasName(obj.name)
        self.assertHasDescription(obj.description)
        self.assertHasFilename(obj.filename)
        self.assertHasAttributeDateTime('created_on_datetime', obj.created_on_datetime)
        self.assertHasRelationshipAuthor()
        # self.assertHasRelationshipHolders()
        return self


class BadgeCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(BadgeCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(BadgeResponse(data_))
        self['data'] = datas
