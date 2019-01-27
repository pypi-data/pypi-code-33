# -*- coding: utf-8 -*-

from .base import BaseResponse
from .collections import BaseCollectionResponse


class MoveTypeResponse(BaseResponse):

    def assertHasPublicAttributes(self, obj):
        self.assertHasAttribute('name', obj.name)
        # self.assertHasRelationshipMoves()  # # Seems not supported by framework
        return self


class MovesTypesCollectionResponse(BaseCollectionResponse):

    def __init__(self, data):
        super(MovesTypesCollectionResponse, self).__init__(data)
        datas = []
        for data_ in self.data:
            datas.append(MoveTypeResponse(data_))
        self['data'] = datas
