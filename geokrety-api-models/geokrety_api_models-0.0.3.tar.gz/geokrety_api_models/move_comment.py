# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import bleach
import characterentities
from geokrety_api_exceptions.json_api import GKUnprocessableEntity

from .base import Base
from .utilities.const import (MOVE_COMMENT_TYPE_MISSING, MOVE_TYPE_ARCHIVED,
                              MOVE_TYPE_DROPPED, MOVE_TYPE_SEEN,
                              MOVE_TYPES_TEXT)


class MoveComment(Base):
    __tablename__ = 'gk-ruchy-comments'

    id = Column(
        'comment_id',
        Integer,
        primary_key=True,
        key='id',
    )

    move_id = Column(
        'ruch_id',
        Integer,
        ForeignKey('gk-ruchy.id'),
        key='move_id',
        nullable=False,
    )

    move = relationship(
        "Move",
        foreign_keys=[move_id],
        backref="comments",
    )

    author_id = Column(
        'user_id',
        Integer,
        ForeignKey('gk-users.id', name='fk_move_comment_author'),
        key='author_id',
        nullable=False,
    )

    author = relationship(
        "User",
        foreign_keys=[author_id],
        backref="moves_comments",
    )

    geokret_id = Column(
        'kret_id',
        Integer,
        ForeignKey('gk-geokrety.id', name='fk_move_comment_geokret'),
        key='geokret_id',
        nullable=False,
    )

    created_on_datetime = Column(
        'data_dodania',
        DateTime,
        key='created_on_datetime',
        nullable=False,
        default=datetime.datetime.utcnow,
    )

    updated_on_datetime = Column(
        'timestamp',
        DateTime,
        key='updated_on_datetime',
        nullable=False,
        default=datetime.datetime.utcnow,
    )

    _comment = Column(
        'comment',
        String(1000),
        nullable=False,
    )

    type = Column(
        Integer,
        nullable=False,
        default=0,
    )

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

    def is_missing_authorized(self):
        if self.type != MOVE_COMMENT_TYPE_MISSING:
            return True
        if self.move.geokret.last_position is not None and \
                self.move.geokret.last_position.id != self.move.id:
            raise GKUnprocessableEntity("Cannot declare 'missing' on old moves",
                                        {'pointer': '/data/relationships/move/data'})
        if self.move.type in [MOVE_TYPE_DROPPED,
                              MOVE_TYPE_SEEN,
                              MOVE_TYPE_ARCHIVED]:
            return True
        raise GKUnprocessableEntity("Cannot declare 'missing' on move_type %s" %
                                    MOVE_TYPES_TEXT[self.move.type],
                                    {'pointer': '/data/relationships/move/data'})


@event.listens_for(MoveComment, 'before_insert')
def before_insert_listener(mapper, connection, target):
    target.geokret_id = target.move.geokret.id
    target.is_missing_authorized()


@event.listens_for(MoveComment, "before_update")
def before_update(mapper, connection, target):
    target.is_missing_authorized()
