# -*- coding: utf-8 -*-

from .base import BaseResponse
from .collections import BaseCollectionResponse


class GeokretTypeResponse(BaseResponse):

    def assertHasPublicAttributes(self, obj):
        self.assertHasAttribute('name', obj.name)
        # self.assertHasRelationshipGeokrety()  # # Seems not supported by framework
        return self


class GeokretyTypesCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(GeokretyTypesCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(GeokretTypeResponse(data_))
        self['data'] = datas
