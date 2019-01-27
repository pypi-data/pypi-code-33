from app.api.helpers.data_layers import MovesTypeDataLayer
from app.api.schema.moves_types import MovesTypesSchema
from flask_rest_jsonapi import ResourceDetail, ResourceList


class MovesTypeList(ResourceList):

    methods = ['GET']
    schema = MovesTypesSchema
    data_layer = {
        'class': MovesTypeDataLayer
    }


class MovesTypeDetail(ResourceDetail):

    methods = ['GET']
    schema = MovesTypesSchema
    data_layer = {
        'class': MovesTypeDataLayer
    }
