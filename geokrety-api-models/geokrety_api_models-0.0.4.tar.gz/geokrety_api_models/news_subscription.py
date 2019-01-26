# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import (Column, Date, DateTime, ForeignKey,
                        ForeignKeyConstraint, Integer)
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base


class NewsSubscription(Base):
    __tablename__ = 'gk-news-comments-access'

    id = Column(
        Integer,
        primary_key=True,
    )

    news_id = Column(
        Integer,
        ForeignKey('gk-news.id'),
        nullable=False,
    )

    user_id = Column(
        Integer,
        ForeignKey('gk-users.id', name='fk_news_comment_subscription'),
        nullable=False,
    )

    ForeignKeyConstraint(
        ['author_id'], ['user.id'],
        use_alter=True,
        name='fk_news_comment_subscription'
    )

    subscribed_on_datetime = Column(
        'read',
        DateTime,
        key='subscribed_on_datetime',
        nullable=False,
        default=datetime.datetime.utcnow,
    )

    post = Column(
        Date,
        nullable=True,
    )

    _subscribed = Column(
        'subscribed',
        Integer,
        key='subscribed',
        default=1,
    )

    @hybrid_property
    def subscribed(self):
        """
        Hybrid property for subscribed
        :return:
        """
        return bool(self._subscribed)

    @subscribed.setter
    def subscribed(self, subscribed):
        """
        Setter for _subscribed, convert integer to boolean
        :param subscribed:
        :return:
        """
        self._subscribed = bool(subscribed)
