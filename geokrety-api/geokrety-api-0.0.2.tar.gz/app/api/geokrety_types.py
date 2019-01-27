from flask_jwt import current_identity
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)

from app.api.helpers.data_layers import GeoKretyTypeDataLayer
from app.api.schema.geokrety_types import GeoKretyTypesSchema


class GeokretTypeList(ResourceList):

    methods = ['GET']
    schema = GeoKretyTypesSchema
    data_layer = {
        'class': GeoKretyTypeDataLayer
    }


class GeokretTypeDetail(ResourceDetail):

    methods = ['GET']
    schema = GeoKretyTypesSchema
    data_layer = {
        'class': GeoKretyTypeDataLayer
    }


class GeokretTypeRelationship(ResourceRelationship):
    methods = ['GET']
    schema = GeoKretyTypesSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'class': GeoKretyTypeDataLayer
    }
