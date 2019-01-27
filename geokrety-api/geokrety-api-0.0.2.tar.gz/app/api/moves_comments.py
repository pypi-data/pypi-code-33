# -*- coding: utf-8 -*-

from flask import current_app
from flask_jwt import current_identity
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)

from app.api.bootstrap import api
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.permission_manager import has_access
from app.api.schema.moves_comments import MoveCommentSchema
from app.models import db
from geokrety_api_models import MoveComment
from geokrety_api_models.utilities.move_tasks import update_geokret_and_moves


class MoveCommentList(ResourceList):

    def before_post(self, args, kwargs, data=None):
        # Defaults to current user
        if 'author' not in data:
            data['author'] = str(current_identity.id)

        if has_access('is_admin'):
            return

        # Check author_id
        if data.get('author') != str(current_identity.id):
            raise UnprocessableEntity("Author Relationship override disallowed",
                                     {'pointer': '/data/relationships/author/data'})

    def create_object(self, data, kwargs):
        move_comment = super(MoveCommentList, self).create_object(data, kwargs)
        if not current_app.config['ASYNC_OBJECTS_ENHANCEMENT']:
            update_geokret_and_moves(db.session, move_comment.move.geokret.id)
        return move_comment

    methods = ['GET', 'POST']
    decorators = (
        api.has_permission('auth_required', methods="POST"),
    )
    schema = MoveCommentSchema
    data_layer = {
        'session': db.session,
        'model': MoveComment,
    }


class MoveCommentDetail(ResourceDetail):

    def before_patch(self, args, kwargs, data=None):
        if has_access('is_admin'):
            return

        # Check author_id
        if data.get('author', str(current_identity.id)) != str(current_identity.id):
            raise UnprocessableEntity('Author must be yourself',
                                     {'pointer': '/data/relationships/author/data'})

    def update_object(self, data, qs, kwargs):
        move_comment = super(MoveCommentDetail, self).update_object(data, qs, kwargs)
        if not current_app.config['ASYNC_OBJECTS_ENHANCEMENT']:
            update_geokret_and_moves(db.session, move_comment.move.geokret.id)
        return move_comment

    def delete_object(self, data):
        move_comment_deleted_geokret_id = self._data_layer.get_object(data).move.geokret.id
        super(MoveCommentDetail, self).delete_object(data)
        if not current_app.config['ASYNC_OBJECTS_ENHANCEMENT']:
            update_geokret_and_moves(db.session, move_comment_deleted_geokret_id)

    methods = ['GET', 'PATCH', 'DELETE']
    decorators = (
        api.has_permission('is_move_comment_author', methods="PATCH,DELETE",
                           fetch="id", fetch_as="move_comment_id", model=MoveComment),
    )
    schema = MoveCommentSchema
    data_layer = {
        'session': db.session,
        'model': MoveComment,
    }


class MoveCommentRelationship(ResourceRelationship):
    methods = ['GET']
    schema = MoveCommentSchema
    data_layer = {'session': db.session,
                  'model': MoveComment}
