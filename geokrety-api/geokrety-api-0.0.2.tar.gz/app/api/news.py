from flask_jwt import current_identity
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.schema.news import NewsSchema
from app.models import db
from geokrety_api_models import News, NewsComment, NewsSubscription


class NewsList(ResourceList):

    def query(self, view_kwargs):
        """Filter news"""
        query_ = self.session.query(News)
        return query_

    def before_post(self, args, kwargs, data=None):
        # Enforce author to current user
        if 'author' not in data or not data['author']:
            data['author'] = current_identity.id

        # Enforce username to current user if undefined
        if 'username' not in data or not data['username']:
            data['username'] = current_identity.name

    schema = NewsSchema
    get_schema_kwargs = {'context': {'current_identity': current_identity}}
    decorators = (
        api.has_permission('is_admin', methods="POST"),
    )
    data_layer = {
        'session': db.session,
        'model': News,
        'methods': {
            'query': query
        }
    }


class NewsDetail(ResourceDetail):

    def before_get_object(self, view_kwargs):
        """
        before get method for news object
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('news_comment_id') is not None:
            news_comment = safe_query(self, NewsComment, 'id', view_kwargs['news_comment_id'], 'news_comment_id')
            view_kwargs['id'] = news_comment.news_id

        if view_kwargs.get('news_subscription_id') is not None:
            news_subscription = safe_query(self, NewsSubscription, 'id',
                                           view_kwargs['news_subscription_id'], 'news_subscription_id')
            view_kwargs['id'] = news_subscription.news_id

    def before_patch(self, args, kwargs, data=None):
        # Enforce author to current user
        if 'author' not in data or not data['author']:
            data['author'] = current_identity.id

        # Enforce username to current user if undefined
        if 'username' not in data or not data['username']:
            data['username'] = current_identity.name

    decorators = (
        api.has_permission('is_admin', methods="PATCH,DELETE"),
    )
    schema = NewsSchema
    data_layer = {
        'session': db.session,
        'model': News,
        'methods': {
            'before_get_object': before_get_object
        }
    }


class NewsRelationship(ResourceRelationship):
    methods = ['GET']
    schema = NewsSchema
    data_layer = {
        'session': db.session,
        'model': News
    }
