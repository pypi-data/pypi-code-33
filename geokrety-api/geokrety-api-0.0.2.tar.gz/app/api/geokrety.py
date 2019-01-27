

from datetime import datetime

from flask import request
from flask_jwt import current_identity
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)
from flask_rest_jsonapi.exceptions import JsonApiException, ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.data_layers import GEOKRETY_TYPES_LIST, MOVE_TYPE_DIPPED
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import require_relationship
from app.api.schema.geokrety import GeokretSchemaCreate, GeokretSchemaPublic
from app.models import db
from app.views.regex import REG_LATITUDE, REG_LONGITUDE
from geokrety_api_models import Geokret, Move, User


class GeokretList(ResourceList):

    def query(self, view_kwargs):
        """Filter geokrety"""
        query_ = self.session.query(Geokret)

        # /users/<int:owner_id>/geokrety-owned
        if view_kwargs.get('owner_id') is not None:
            safe_query(self, User, 'id', view_kwargs['owner_id'], 'owner_id')
            query_ = query_.filter_by(owner_id=view_kwargs['owner_id'])

        # /users/<int:holder_id>/geokrety-held
        if view_kwargs.get('holder_id') is not None:
            safe_query(self, User, 'id', view_kwargs['holder_id'], 'holder_id')
            query_ = query_.filter_by(holder_id=view_kwargs['holder_id'])

        # /geokrety-types/<int:geokrety_type_id>/geokrety
        if view_kwargs.get('geokrety_type_id') is not None:
            if str(view_kwargs['geokrety_type_id']) not in GEOKRETY_TYPES_LIST:
                raise ObjectNotFound(u"{}: {} not found".format('GeokretyType', view_kwargs['geokrety_type_id']), {
                                     u'pointer': '{}'.format('geokrety_type_id')})
            query_ = query_.filter_by(type=str(view_kwargs['geokrety_type_id']))

        return query_

    def post(self, *args, **kwargs):
        self.schema = GeokretSchemaCreate
        return super(GeokretList, self).post(args, kwargs)

    def before_post(self, args, kwargs, data=None):
        # Enforce owner to current user
        if not current_identity.is_admin or 'owner' not in data:
            data['owner'] = current_identity.id

        require_relationship(['type'], data)

        # Enforce holder to owner
        data['holder'] = data['owner']

        if 'born_at_home' in data and data['born_at_home']:
            self._data_layer.__create_first_move = True
            del data['born_at_home']
        else:
            self._data_layer.__create_first_move = False

    def after_create_object(self, geokret, data, view_kwargs):
        # Create first move if requested
        if self.__create_first_move:
            # But only if user has home coordinates
            if geokret.owner.latitude and geokret.owner.longitude:
                move = Move(
                    author=geokret.owner,
                    geokret=geokret,
                    type=MOVE_TYPE_DIPPED,
                    moved_on_datetime=datetime.utcnow(),
                    latitude=geokret.owner.latitude,
                    longitude=geokret.owner.longitude,
                    comment="Born here",
                )
                geokret.last_move = move
                db.session.add(move)
                db.session.add(geokret)
                try:
                    db.session.commit()
                except Exception as e:  # pragma: no cover
                    db.session.rollback()
                    raise JsonApiException("Failed to create first move: " + str(e), source={'pointer': '/data'})
        return geokret

    schema = GeokretSchemaPublic
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    decorators = (
        api.has_permission('auth_required', methods="POST"),
    )
    data_layer = {
        'session': db.session,
        'model': Geokret,
        'methods': {
            'query': query,
            'after_create_object': after_create_object,
        },
    }


class GeokretInACacheList(GeokretList):

    def query(self, view_kwargs):
        """Filter geokrety"""
        query_ = self.session.query(Geokret)

        waypoint = request.args.get('waypoint')
        if waypoint is not None:
            if waypoint:
                return query_.filter(Geokret.last_position.has(Move.waypoint == waypoint))
            raise UnprocessableEntity("Waypoint is invalid",
                                      {'pointer': '/argument/waypoint'})

        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        if latitude and longitude:
            if not REG_LATITUDE.match(str(latitude)):
                raise UnprocessableEntity("Latitude is invalid",
                                          {'pointer': '/argument/latitude'})
            if not REG_LONGITUDE.match(str(longitude)):
                raise UnprocessableEntity("Longitude is invalid",
                                          {'pointer': '/argument/longitude'})
            return query_\
                .filter(Geokret.last_position.has(Move.latitude == latitude))\
                .filter(Geokret.last_position.has(Move.latitude == latitude))

        raise UnprocessableEntity("Waypoint or latitude/longitude missing from arguments",
                                  {'pointer': '/argument/[waypoint or latitude-longitude]'})

    methods = ('GET',)
    data_layer = {
        'session': db.session,
        'model': Geokret,
        'methods': {
            'query': query,
        },
    }


class GeokretDetail(ResourceDetail):
    def before_patch(self, args, kwargs, data=None):
        data.pop('holder', None)
        data.pop('moves', None)

        if not has_access('is_admin'):
            data.pop('owner', None)

    decorators = (
        api.has_permission('is_geokret_owner', methods="PATCH,DELETE",
                           fetch="id", fetch_as="geokret_id",
                           model=Geokret, fetch_key_url="id"),
    )
    methods = ('GET', 'PATCH', 'DELETE')
    schema = GeokretSchemaPublic
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'session': db.session,
        'model': Geokret,
    }


class GeokretRelationship(ResourceRelationship):
    methods = ['GET']
    schema = GeokretSchemaPublic
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'session': db.session,
        'model': Geokret,
    }
