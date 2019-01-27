# -*- coding: utf-8 -*-

from geokrety_api_models import User

from .base import BaseResponse
from .collections import BaseCollectionResponse


class GeokretResponse(BaseResponse):

    def assertHasTrackingCode(self, tracking_code):
        self.assertHasAttribute('tracking-code', tracking_code)
        return self

    def assertHasRelationshipOwner(self):
        self.assertHasRelationshipSelf('owner', '/v1/geokrety/%s/relationships/owner' % self.id)
        self.assertHasRelationshipRelated('owner', '/v1/geokrety/%s/owner' % self.id)
        return self

    def assertHasRelationshipHolder(self):
        self.assertHasRelationshipSelf('holder', '/v1/geokrety/%s/relationships/holder' % self.id)
        self.assertHasRelationshipRelated('holder', '/v1/geokrety/%s/holder' % self.id)
        return self

    def assertHasRelationshipGeokretyType(self):
        self.assertHasRelationshipSelf('type', '/v1/geokrety/%s/relationships/type' % self.id)
        self.assertHasRelationshipRelated('type', '/v1/geokrety/%s/type' % self.id)
        return self

    def assertHasRelationshipMoves(self):
        self.assertHasRelationshipSelf('moves', '/v1/geokrety/%s/relationships/moves' % (self.id))
        self.assertHasRelationshipRelated('moves', '/v1/geokrety/%s/moves' % (self.id))
        return self

    def assertHasRelationshipLastPosition(self):
        self.assertHasRelationshipSelf('last-position', '/v1/geokrety/%s/relationships/last-position' % (self.id))
        self.assertHasRelationshipRelated('last-position', '/v1/geokrety/%s/last-position' % (self.id))
        return self

    def assertHasRelationshipLastMove(self):
        self.assertHasRelationshipSelf('last-move', '/v1/geokrety/%s/relationships/last-move' % (self.id))
        self.assertHasRelationshipRelated('last-move', '/v1/geokrety/%s/last-move' % (self.id))
        return self

    def assertHasRelationshipOwnerData(self, user):
        user_id = user.id if isinstance(user, User) else user
        self.assertHasRelationshipData('owner', user_id, 'user')
        return self

    def assertHasRelationshipHolderData(self, user):
        user_id = user.id if isinstance(user, User) else user
        self.assertHasRelationshipData('holder', user_id, 'user')
        return self

    def assertHasRelationshipGeokretyTypeData(self, type_id):
        self.assertHasRelationshipData('type', type_id, 'geokrety-type')
        return self

    def assertHasRelationshipMovesDatas(self, moves_ids):
        self.assertHasRelationshipDatas('moves', moves_ids, 'move')
        return self

    def assertHasRelationshipLastPositionData(self, move_id):
        self.assertHasRelationshipData('last-position', move_id, 'move')
        return self

    def assertHasRelationshipLastMoveData(self, move_id):
        self.assertHasRelationshipData('last-move', move_id, 'move')
        return self

    def assertHasPublicAttributes(self, obj):
        self.assertHasAttribute('name', obj.name)
        self.assertHasAttribute('description', obj.description)
        self.assertHasAttribute('missing', obj.missing)
        # self.assertHasAttribute('archived', obj.archived)  # TODO
        self.assertHasAttribute('distance', obj.distance)
        self.assertHasAttribute('caches-count', obj.caches_count)
        self.assertHasAttribute('pictures-count', obj.pictures_count)
        self.assertHasAttribute('average-rating', obj.average_rating)
        # self.assertHasAttribute('country-track', obj.country_track)  # TODO
        self.assertHasRelationshipOwner()
        self.assertHasRelationshipHolder()
        self.assertHasRelationshipMoves()
        self.assertHasRelationshipLastPosition()
        self.assertHasRelationshipLastMove()
        self.assertHasRelationshipGeokretyType()
        self.assertHasRelationshipGeokretyTypeData(obj.type)
        return self


class GeokretyCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(GeokretyCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(GeokretResponse(data_))
        self['data'] = datas
