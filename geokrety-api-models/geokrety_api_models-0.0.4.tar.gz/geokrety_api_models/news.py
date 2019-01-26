# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import bleach
import characterentities

from .base import Base


class News(Base):
    __tablename__ = 'gk-news'

    id = Column(
        'news_id',
        Integer,
        primary_key=True,
        key='id'
    )
    _title = Column(
        'tytul',
        String(50),
        key='title',
        nullable=False
    )
    _content = Column(
        'tresc',
        Text,
        key='content',
        nullable=False
    )
    _username = Column(
        'who',
        String(80),
        key='username',
        nullable=True
    )
    author_id = Column(
        'userid',
        Integer,
        ForeignKey('gk-users.id'),
        key='author_id',
        nullable=False,
    )
    comments_count = Column(
        'komentarze',
        Integer,
        key='comments_count',
        default=0
    )
    last_comment_datetime = Column(
        'ostatni_komentarz',
        DateTime,
        key='last_comment_datetime',
        nullable=False,
        default="0000-00-00T00:00:00"
    )
    created_on_datetime = Column(
        'date',
        DateTime,
        key='created_on_datetime',
        default=datetime.datetime.utcnow
    )
    czas_postu = Column(
        DateTime,
        default="0000-00-00T00:00:00"
    )

    # author = relationship('User', backref=backref('news'))
    comments = relationship(
        'NewsComment',
        backref="news",
        cascade="all,delete"
    )
    subscriptions = relationship(
        'NewsSubscription',
        backref="news",
        cascade="all,delete"
    )

    @hybrid_property
    def title(self):
        return characterentities.decode(self._title)

    @title.setter
    def title(self, title):
        title_clean = bleach.clean(title, tags=[], strip=True)
        self._title = characterentities.decode(title_clean).strip()

    @title.expression
    def title(cls):
        return cls._title

    @hybrid_property
    def content(self):
        return characterentities.decode(self._content)

    @content.setter
    def content(self, content):
        # Drop all unallowed html tags
        content_clean = bleach.clean(content, strip=True)
        # Strip spaces
        self._content = characterentities.decode(content_clean).strip()

    @content.expression
    def content(cls):
        return cls._content

    @hybrid_property
    def username(self):
        if self._username:
            return characterentities.decode(self._username)

    @username.setter
    def username(self, username):
        username_clean = bleach.clean(username, tags=[], strip=True)
        self._username = characterentities.decode(username_clean).strip()

    @username.expression
    def username(cls):
        return cls._username
