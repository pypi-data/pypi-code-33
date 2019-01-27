from flask_jwt import current_identity
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.api.schema.users import UserSchema
from app.models import db
from geokrety_api_models import (Badge, Geokret, Move, MoveComment, News,
                                 NewsComment, NewsSubscription, User)


class UserList(ResourceList):

    decorators = (
        api.has_permission('is_anonymous', methods="POST"),
    )
    schema = UserSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'session': db.session,
        'model': User,
    }


class UserDetail(ResourceDetail):

    def before_get_object(self, view_kwargs):
        """
        before get method for user object
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('news_id') is not None:
            news = safe_query(self, News, 'id', view_kwargs['news_id'], 'news_id')
            view_kwargs['id'] = news.author_id

        if view_kwargs.get('news_comment_id') is not None:
            news_comment = safe_query(self, NewsComment, 'id', view_kwargs['news_comment_id'], 'news_comment_id')
            view_kwargs['id'] = news_comment.author_id

        if view_kwargs.get('news_subscription_id') is not None:
            news_subscription = safe_query(self, NewsSubscription, 'id',
                                           view_kwargs['news_subscription_id'], 'news_subscription_id')
            view_kwargs['id'] = news_subscription.user_id

        if view_kwargs.get('geokret_owned_id') is not None:
            geokret = safe_query(self, Geokret, 'id', view_kwargs['geokret_owned_id'], 'geokret_owned_id')
            view_kwargs['id'] = geokret.owner_id

        if view_kwargs.get('geokret_held_id') is not None:
            geokret = safe_query(self, Geokret, 'id', view_kwargs['geokret_held_id'], 'geokret_held_id')
            view_kwargs['id'] = geokret.holder_id

        if view_kwargs.get('move_id') is not None:
            move = safe_query(self, Move, 'id', view_kwargs['move_id'], 'move_id')
            view_kwargs['id'] = move.author_id

        if view_kwargs.get('move_comment_id') is not None:
            move_comment = safe_query(self, MoveComment, 'id', view_kwargs['move_comment_id'], 'move_comment_id')
            view_kwargs['id'] = move_comment.author_id

        if view_kwargs.get('badge_author_id') is not None:
            badge = safe_query(self, Badge, 'id', view_kwargs['badge_author_id'], 'badge_author_id')
            view_kwargs['id'] = badge.author_id

    def before_delete(self, args, kwargs):
        # Restrict deleting to admin only
        if not has_access('is_admin'):
            raise ForbiddenException('Access Forbidden', {'source': ''})

    current_identity = current_identity
    decorators = (
        api.has_permission('is_user_itself', methods="PATCH,DELETE",
                           fetch="id", fetch_as="user_id",
                           model=User, fetch_key_url="id"),
    )
    methods = ('GET', 'PATCH', 'DELETE')
    schema = UserSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'session': db.session,
        'model': User,
        'methods': {
            'before_get_object': before_get_object,
        },
    }


class UserRelationship(ResourceRelationship):
    methods = ['GET']
    schema = UserSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    data_layer = {
        'session': db.session,
        'model': User,
    }
