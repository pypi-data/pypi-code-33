# -*- coding: utf-8 -*-

from geokrety_api_models import Geokret, User

from .base import BaseResponse
from .collections import BaseCollectionResponse


class MoveResponse(BaseResponse):

    def assertHasRelationshipAuthor(self):
        self.assertHasRelationshipSelf('author', '/v1/moves/%s/relationships/author' % self.id)
        self.assertHasRelationshipRelated('author', '/v1/moves/%s/author' % self.id)
        return self

    def assertHasRelationshipMoveType(self):
        self.assertHasRelationshipSelf('type', '/v1/moves/%s/relationships/type' % self.id)
        self.assertHasRelationshipRelated('type', '/v1/moves/%s/type' % self.id)
        return self

    def assertHasRelationshipGeokret(self):
        self.assertHasRelationshipSelf('geokret', '/v1/moves/%s/relationships/geokret' % self.id)
        self.assertHasRelationshipRelated('geokret', '/v1/moves/%s/geokret' % self.id)
        return self

    def assertHasRelationshipAuthorData(self, user):
        user_id = user.id if isinstance(user, User) else user
        self.assertHasRelationshipData('author', user_id, 'user')
        return self

    def assertHasRelationshipMoveTypeData(self, type_id):
        self.assertHasRelationshipData('type', type_id, 'move-type')
        return self

    def assertHasRelationshipGeokretData(self, geokret):
        geokret_id = geokret.id if isinstance(geokret, Geokret) else geokret
        self.assertHasRelationshipData('geokret', geokret_id, 'geokret')
        return self

    def assertHasPublicAttributes(self, obj):
        self.assertHasAttribute('comment', obj.comment)
        self.assertHasAttribute('username', obj.username)
        self.assertHasAttributeDateTime('moved_on_datetime', obj.moved_on_datetime)
        self.assertHasAttribute('application_name', obj.application_name)
        self.assertHasAttribute('application_version', obj.application_version)
        self.assertHasAttribute('pictures_count', obj.pictures_count)
        self.assertHasAttribute('comments_count', obj.comments_count)
        self.assertHasAttributeDateTime('created_on_datetime', obj.created_on_datetime)
        self.assertHasAttributeDateTime('updated_on_datetime', obj.updated_on_datetime)
        self.assertHasRelationshipAuthor()
        self.assertHasRelationshipMoveType()
        self.assertHasRelationshipGeokret()
        self.assertHasRelationshipAuthorData(obj.author.id)
        self.assertHasRelationshipMoveTypeData(obj.type)
        self.assertHasRelationshipGeokretData(obj.geokret.id)
        with self.assertRaises(AssertionError):
            self.get_attribute('tracking_code')
        return self


class MovesCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(MovesCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(MoveResponse(data_))
        self['data'] = datas
