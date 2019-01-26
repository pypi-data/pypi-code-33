# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import (Column, DateTime, ForeignKey,
                        ForeignKeyConstraint, Integer, String)
from sqlalchemy.ext.hybrid import hybrid_property

import bleach
import characterentities

from .base import Base


class NewsComment(Base):
    __tablename__ = 'gk-news-comments'

    id = Column(
        'comment_id',
        Integer,
        primary_key=True,
        key='id'
    )

    news_id = Column(
        'news_id',
        Integer,
        ForeignKey('gk-news.id'),
        key='news_id',
        nullable=False
    )

    author_id = Column(
        'user_id',
        Integer,
        ForeignKey('gk-users.id', name='fk_news_comment_author'),
        key='author_id',
        nullable=False
    )

    ForeignKeyConstraint(
        ['author_id'], ['user.id'],
        use_alter=True,
        name='fk_news_comment_author'
    )

    created_on_datetime = Column(
        'date',
        DateTime,
        key='created_on_datetime',
        nullable=False,
        default=datetime.datetime.utcnow
    )

    _comment = Column(
        'comment',
        String(1000),
        nullable=False
    )

    icon = Column(
        Integer,
        default=0
    )

    # news = relationship('News', backref=backref('news_comments'))
    # author = relationship('User', backref=backref('news_comments'))

    @hybrid_property
    def comment(self):
        return characterentities.decode(self._comment)

    @comment.setter
    def comment(self, comment):
        # Drop all html tags
        comment_clean = bleach.clean(comment, strip=True)
        # Strip spaces
        self._comment = characterentities.decode(comment_clean).strip()

    @comment.expression
    def comment(cls):
        return cls._comment
