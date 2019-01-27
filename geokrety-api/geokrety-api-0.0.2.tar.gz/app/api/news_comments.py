from flask_jwt import current_identity
from flask_rest_jsonapi import (ResourceDetail, ResourceList,
                                ResourceRelationship)

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.api.schema.news_comments import NewsCommentSchema
from app.models import db
from geokrety_api_models import News, NewsComment, NewsSubscription, User


class NewsCommentList(ResourceList):

    def query(self, view_kwargs):
        """Filter news-comments"""
        query_ = self.session.query(NewsComment)

        if view_kwargs.get('news_id') is not None:
            safe_query(self, News, 'id', view_kwargs['news_id'], 'news_id')
            query_ = query_.join(News).filter(News.id == view_kwargs['news_id'])

        if view_kwargs.get('author_id') is not None:
            safe_query(self, User, 'id', view_kwargs['author_id'], 'author_id')
            query_ = query_.join(User).filter(User.id == view_kwargs['author_id'])

        return query_

    def before_post(self, args, kwargs, data=None):
        user = current_identity

        self.subscribe = data.pop('subscribe', False)

        # Defaults to current user
        if 'author' not in data:
            data['author'] = str(user.id)

        if has_access('is_admin'):
            return

        # Check author_id
        if data.get('author') != str(user.id):
            raise ForbiddenException('Author must be yourself',
                                     {'pointer': '/data/relationships/author/data'})

    def create_object(self, data, kwargs):
        news_comment = super(NewsCommentList, self).create_object(data, kwargs)

        # Create first move if requested
        if self.subscribe:
            news_subscription = NewsSubscription(
                news_id=news_comment.news_id,
                user_id=news_comment.author_id,
                subscribed=True,
            )
            db.session.add(news_subscription)
            db.session.commit()
        return news_comment

    def after_create_object(self, obj, data, view_kwargs):
        # Increment comment count on news
        news = safe_query(self, News, 'id', obj.news_id, 'id')
        news.comments_count += 1
        save_to_db(news)

    decorators = (
        api.has_permission('auth_required', methods="POST"),
    )
    schema = NewsCommentSchema
    data_layer = {
        'session': db.session,
        'model': NewsComment,
        'methods': {
            'query': query,
            'after_create_object': after_create_object
        }
    }


class NewsCommentDetail(ResourceDetail):

    def before_patch(self, args, kwargs, data=None):
        user = current_identity

        self.subscribe = data.pop('subscribe', None)

        if has_access('is_admin'):
            return

        # Check author_id
        if data.get('author', str(user.id)) != str(user.id):
            raise ForbiddenException('Author must be yourself',
                                     {'pointer': '/data/relationships/author/data'})

    def update_object(self, data, qs, kwargs):
        news_comment = super(NewsCommentDetail, self).update_object(data, qs, kwargs)

        # Create subscription if requested
        if self.subscribe:
            news_subscription = NewsSubscription(
                news_id=news_comment.news_id,
                user_id=news_comment.author_id,
                subscribed=True,
            )
            db.session.add(news_subscription)
            db.session.commit()
        elif self.subscribe is False:
            news_subscription = db.session \
                .query(NewsSubscription) \
                .filter(
                    NewsSubscription.user_id == news_comment.author_id,
                    NewsSubscription.news_id == news_comment.news_id
                )
            if news_subscription.count():
                db.session.delete(news_subscription.one())
                db.session.commit()
        return news_comment

    def after_delete_object(self, obj, view_kwargs):
        # Decrement comment count on news
        news = safe_query(self, News, 'id', obj.news_id, 'id')
        news.comments_count -= 1
        save_to_db(news)

        # Drop subscriptions
        news_subscription = db.session \
            .query(NewsSubscription) \
            .filter(
                NewsSubscription.user_id == obj.author_id,
                NewsSubscription.news_id == obj.news_id
            )
        if news_subscription.count():
            db.session.delete(news_subscription.one())
            db.session.commit()

    decorators = (
        api.has_permission('is_user_itself', methods="PATCH,DELETE",
                           fetch="author_id", fetch_as="user_id", model=NewsComment),
    )
    schema = NewsCommentSchema
    data_layer = {
        'session': db.session,
        'model': NewsComment,
        'methods': {
            'after_delete_object': after_delete_object
        }
    }


class NewsCommentRelationship(ResourceRelationship):
    methods = ['GET']
    schema = NewsCommentSchema
    data_layer = {'session': db.session,
                  'model': NewsComment}
