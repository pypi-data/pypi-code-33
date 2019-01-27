# -*- coding: utf-8 -*-

from base import BasePayload


class GeokretTypePayload(BasePayload):
    _url = "/v1/geokrety-types/{}"
    _url_collection = "/v1/geokrety-types"
    _response_type = 'GeokretTypeResponse'
    _response_type_collection = 'GeokretyTypesCollectionResponse'

    def __init__(self, *args, **kwargs):
        super(GeokretTypePayload, self).__init__('geokret-type', *args, **kwargs)
