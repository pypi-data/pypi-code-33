import numbers

from flask import current_app, request
from flask_jwt import current_identity
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)

from app.api.bootstrap import api
from app.api.helpers.data_layers import (MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT,
                                         MOVE_TYPE_DIPPED, MOVE_TYPE_DROPPED,
                                         MOVE_TYPE_GRABBED, MOVE_TYPE_SEEN)
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import ForbiddenException, UnprocessableEntity
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import has_relationships
from app.api.schema.moves import (DefaultMoveSchema, MoveArchiveSchema,
                                  MoveCommentSchema, MoveDippedSchema,
                                  MoveDroppedSchema, MoveGrabbedSchema,
                                  MoveSeenSchema)
from app.models import db
from geokrety_api_models import Geokret, Move, MoveComment
from geokrety_api_models.utilities.move_tasks import update_geokret_and_moves


def get_move_type_id(json_data):
    if has_relationships(json_data, 'type'):
        return json_data['data']['relationships']['type']['data']['id']
    raise UnprocessableEntity("Move Type is missing",
                              {'pointer': '/data/relationships/type'})


def get_schema_by_move_type(move_type_id):
    if move_type_id == MOVE_TYPE_GRABBED:
        return MoveGrabbedSchema
    if move_type_id == MOVE_TYPE_COMMENT:
        return MoveCommentSchema
    if move_type_id == MOVE_TYPE_ARCHIVED:
        return MoveArchiveSchema
    if move_type_id == MOVE_TYPE_DROPPED:
        return MoveDroppedSchema
    if move_type_id == MOVE_TYPE_SEEN:
        return MoveSeenSchema
    if move_type_id == MOVE_TYPE_DIPPED:
        return MoveDippedSchema

    raise UnprocessableEntity("Move Type Id is invalid",
                              {'pointer': '/data/attributes/type'})


class MovesList(ResourceList):

    def post(self, *args, **kwargs):
        json_data = request.get_json()

        if 'data' in json_data:
            # Configure schema dynamically
            self.schema = get_schema_by_move_type(get_move_type_id(json_data))

            # Only admins can update author
            if not has_access('is_admin') and has_relationships(json_data, 'author'):
                raise ForbiddenException("Author Relationship override disallowed",
                                         {'pointer': '/data/relationships/author'})

        return super(MovesList, self).post(args, kwargs)

    def before_post(self, args, kwargs, data=None):
        # Don't leave tracking_code as it doesn't exists in database
        if 'tracking_code' in data:
            tracking_code = data['tracking_code']
            del data['tracking_code']

        # Don't leave longitude if no latitude provided
        if 'latitude' not in data or not isinstance(data['latitude'], numbers.Number):
            data.pop('longitude', None)

        # Don't leave latitude if no longitude provided
        if 'longitude' not in data or not isinstance(data['longitude'], numbers.Number):
            data.pop('latitude', None)

        # Move type comment may be selected by GeoKret ID
        if data['type'] == MOVE_TYPE_COMMENT and 'geokret_id' in data:
            self.geokret = safe_query(self, Geokret, 'id', data['geokret_id'], 'geokret-id')
        else:
            # Get GeoKret ID from tracking_code
            self.geokret = safe_query(self, Geokret, 'tracking_code', tracking_code, 'tracking-code')
        data["geokret"] = self.geokret.id

        # Force current connected user as author
        if has_access('is_admin'):
            if "author" not in data:
                data["author"] = current_identity.id
        else:
            data["author"] = current_identity.id

        # Archived move type has special security requirements
        if data['type'] == MOVE_TYPE_ARCHIVED:
            if not has_access('is_geokret_owner', geokret_id=self.geokret.id):
                raise ForbiddenException('Must be the GeoKret Owner', {'pointer': '/data/attributes/geokret-id'})

        if data.get('moved_on_datetime'):
            # Check There is already a move at that date time
            if has_access('is_there_a_move_at_that_datetime',
                          **data):
                raise UnprocessableEntity("There is already a move at that datetime",
                                          {'pointer': '/data/attributes/moved-on-datetime'})

            # Check date time not before GeoKret birth
            if has_access('is_move_before_geokret_birth', **{
                    'geokret_id': self.geokret.id,
                    'moved_on_datetime': data.get('moved_on_datetime'),
            }):
                raise UnprocessableEntity("Move date cannot be prior GeoKret birth date",
                                          {'pointer': '/data/attributes/moved-on-datetime'})

            # Check date time not in the future
            if has_access('is_date_in_the_future',
                          date_time=data.get('moved_on_datetime')):
                raise UnprocessableEntity("Move date and time cannot be in the future",
                                          {'pointer': '/data/attributes/moved-on-datetime'})

    def create_object(self, data, kwargs):
        move = super(MovesList, self).create_object(data, kwargs)
        if not current_app.config['ASYNC_OBJECTS_ENHANCEMENT']:
            update_geokret_and_moves(db.session, move.geokret_id, move.id)
        return move

    schema = DefaultMoveSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    decorators = (
        api.has_permission('auth_required', methods="POST"),
    )

    data_layer = {
        'session': db.session,
        'model': Move,
        'methods': {
            # 'before_create_object': before_create_object,
            # 'apply_relationships': apply_relationships,
        },
    }


class MoveDetail(ResourceDetail):

    def before_get_object(self, view_kwargs):
        """
        before get method for user object
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('move_comment_id') is not None:
            move_comment = safe_query(self, MoveComment, 'id', view_kwargs['move_comment_id'], 'move_comment_id')
            view_kwargs['id'] = move_comment.move_id

    def before_marshmallow(self, args, kwargs):
        # Configure schema dynamically
        if request.method == 'PATCH':
            # Skip for patch as we will compare it to the new move type
            return
        move_type = safe_query(self, Move, 'id', kwargs['id'], 'id').type
        self.schema = get_schema_by_move_type(move_type)

    def patch(self, *args, **kwargs):
        json_data = request.get_json()

        if has_relationships(json_data, 'type'):
            # Configure schema according to the new move type
            new_move_type = get_move_type_id(json_data)
            self.schema = get_schema_by_move_type(new_move_type)

            # On PATCH, checks are executed only on existing fields in payload, we
            # need to force include coordinates to activate constrainst checks,
            # but not necessarily for GRABBED move type as coordinates are optionnal
            if 'attributes' not in json_data['data']:
                json_data['data']['attributes'] = {}
            if new_move_type != MOVE_TYPE_GRABBED:
                old_move = safe_query(self, Move, 'id', kwargs['id'], 'id')
                if 'latitude' not in json_data['data']['attributes']:
                    json_data['data']['attributes']['latitude'] = old_move.latitude
                if 'longitude' not in json_data['data']['attributes']:
                    json_data['data']['attributes']['longitude'] = old_move.longitude

        return super(MoveDetail, self).patch(*args, **kwargs)

    def before_patch(self, args, kwargs, data=None):
        # Only admins can update author
        if not has_access('is_admin') and data.get('author'):
            raise ForbiddenException("Author Relationship override disallowed",
                                     {'pointer': '/data/relationships/author'})

        # Only admins can update geokret relationships
        if not has_access('is_admin') and data.get('geokret'):
            raise ForbiddenException("Geokret relationships cannot be changed",
                                     {'pointer': '/data/relationships/geokret'})

        if data.get('moved_on_datetime'):
            # Check There is already a move at that date time
            if has_access('is_there_a_move_at_that_datetime',
                          id=kwargs['id'],
                          **data):
                raise UnprocessableEntity("There is already a move at that datetime",
                                          {'pointer': '/data/attributes/moved-on-datetime'})

            # Check date time not before GeoKret birth
            if has_access('is_move_before_geokret_birth',
                          id=kwargs['id'],
                          **data):
                raise UnprocessableEntity("Move date and time cannot be prior GeoKret birth date",
                                          {'pointer': '/data/attributes/moved-on-datetime'})

            # Check date time not in the future
            if has_access('is_date_in_the_future',
                          date_time=data.get('moved_on_datetime')):
                raise UnprocessableEntity("Move date and time cannot be in the future",
                                          {'pointer': '/data/attributes/moved-on-datetime'})

        # Remove old coordinates
        if data.get('type') == MOVE_TYPE_COMMENT:
            move = safe_query(self, Move, 'id', kwargs['id'], 'id')
            move.latitude = None
            move.longitude = None

    def update_object(self, data, qs, kwargs):
        old_move = safe_query(self, Move, 'id', kwargs.get('id'), 'id')
        geokrety_to_update = []

        # Comming from Comment require tracking-code
        if old_move.type == MOVE_TYPE_COMMENT and not data.get('tracking_code'):
            raise UnprocessableEntity("Tracking code is missing",
                                      {'pointer': '/data/attributes/tracking-code'})
        # Now convert tracking-code to GeoKret ID
        if 'tracking_code' in data:
            geokrety_to_update.append(old_move.geokret.id)
            old_move.geokret = safe_query(self, Geokret, 'tracking_code', data.get('tracking_code'), 'tracking-code')

        # Save update in database
        move = super(MoveDetail, self).update_object(data, qs, kwargs)
        if not current_app.config['ASYNC_OBJECTS_ENHANCEMENT']:
            geokrety_to_update.append(move.geokret.id)
            update_geokret_and_moves(db.session, geokrety_to_update, move.id)
        return move

    def delete_object(self, data):
        move_deleted_geokret_id = self._data_layer.get_object(data).geokret.id
        super(MoveDetail, self).delete_object(data)
        if not current_app.config['ASYNC_OBJECTS_ENHANCEMENT']:
            update_geokret_and_moves(db.session, move_deleted_geokret_id)

    current_identity = current_identity
    decorators = (
        api.has_permission('is_move_author', methods="PATCH,DELETE",
                           fetch="id", fetch_as="move_id",
                           model=Move, fetch_key_url="id"),
    )
    methods = ('GET', 'PATCH', 'DELETE')
    schema = DefaultMoveSchema
    data_layer = {
        'session': db.session,
        'model': Move,
        'methods': {
            'before_get_object': before_get_object,
        },
    }


class MoveRelationship(ResourceRelationship):
    methods = ['GET']
    schema = DefaultMoveSchema
    data_layer = {
        'session': db.session,
        'model': Move,
    }
