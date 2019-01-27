# -*- coding: utf-8 -*-

from base import BasePayload


class MoveTypePayload(BasePayload):
    _url = "/v1/moves-types/{}"
    _url_collection = "/v1/moves-types"
    _response_type = 'MoveTypeResponse'
    _response_type_collection = 'MovesTypesCollectionResponse'

    def __init__(self, *args, **kwargs):
        super(MoveTypePayload, self).__init__('move-type', *args, **kwargs)
