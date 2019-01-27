from flask_jwt import current_identity
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)

from app.api.bootstrap import api
from app.api.schema.badges import BadgeSchema
from app.models import db
from geokrety_api_models.badge import Badge


class BadgeList(ResourceList):

    def before_post(self, args, kwargs, data=None):
        # Defaults to current user
        if 'author' not in data:
            data['author'] = str(current_identity.id)

    decorators = (
        api.has_permission('is_admin', methods="POST"),
    )
    methods = ('GET', 'POST')
    schema = BadgeSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'session': db.session,
        'model': Badge,
    }


class BadgeDetail(ResourceDetail):
    decorators = (
        api.has_permission('is_admin', methods="PATCH,DELETE"),
    )
    methods = ('GET', 'PATCH', 'DELETE')
    schema = BadgeSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'session': db.session,
        'model': Badge,
    }


class BadgeRelationship(ResourceRelationship):
    methods = ('GET',)
    schema = BadgeSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'session': db.session,
        'model': Badge,
    }
