# -*- coding: utf-8 -*-

import random
from datetime import datetime

from sqlalchemy import (TIMESTAMP, Boolean, Column, DateTime, Enum, ForeignKey,
                        Integer, String, Text, event)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

import bleach
import characterentities

from .base import Base
from .move import Move
from .utilities.const import MOVE_TYPE_ARCHIVED, MOVE_TYPE_COMMENT
from .utilities.date import round_microseconds


class Geokret(Base):
    __tablename__ = 'gk-geokrety'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        key='id',
    )
    tracking_code = Column(
        'nr',
        String(9),
        key='tracking_code',
        nullable=False,
        unique=True,
    )
    _name = Column(
        'nazwa',
        String(75),
        key='name',
        nullable=False,
    )
    _description = Column(
        'opis',
        Text(),
        key='description',
        nullable=False,
        default='',
    )
    type = Column(
        'typ',
        Enum('0', '1', '2', '3', '4'),
        key='type',
        nullable=False,
    )
    missing = Column(
        'missing',
        Boolean,
        key='missing',
        nullable=False,
        default=False,
    )
    distance = Column(
        'droga',
        Integer,
        key='distance',
        nullable=False,
        default=0,
    )
    caches_count = Column(
        'skrzynki',
        Integer,
        key='caches_count',
        nullable=False,
        default=0,
    )
    pictures_count = Column(
        'zdjecia',
        Integer,
        key='pictures_count',
        nullable=False,
        default=0,
    )
    created_on_datetime = Column(
        'data',
        DateTime,
        nullable=False,
        key='created_on_datetime',
        default=datetime.utcnow,
    )
    updated_on_datetime = Column(
        'timestamp',
        TIMESTAMP(timezone=True),
        key='updated_on_datetime',
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    owner_id = Column(
        'owner',
        Integer,
        ForeignKey('gk-users.id', name='fk_geokret_owner'),
        nullable=True,
        key='owner_id',
    )
    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        backref="geokrety_owned"
    )

    holder_id = Column(
        'hands_of',
        Integer,
        ForeignKey('gk-users.id', name='fk_geokret_holder'),
        key='holder_id',
    )
    holder = relationship(
        "User",
        foreign_keys=[holder_id],
        backref="geokrety_held"
    )

    # This is used to compute the archived status
    _moves = relationship(
        'Move',
        foreign_keys="Move.geokret_id",
        lazy="dynamic",
    )

    last_position_id = Column(
        'ost_pozycja_id',
        Integer,
        ForeignKey('gk-ruchy.id', name='fk_geokret_last_position'),
        key='last_position_id',
        nullable=True,
        default=None,
    )
    last_position = relationship(
        "Move",
        foreign_keys=[last_position_id],
        backref="spotted_geokret",
        post_update=True
    )

    last_move_id = Column(
        'ost_log_id',
        Integer,
        ForeignKey('gk-ruchy.id', name='fk_last_move', ondelete="SET NULL"),
        key='last_move_id'
    )
    last_move = relationship(
        "Move",
        foreign_keys=[last_move_id],
        backref="moves",
        post_update=True
    )

    # avatar_id = Column(
    #     'avatarid',
    #     Integer,
    #     ForeignKey('gk-obrazki.id'),
    #     key='avatar_id'
    # )

    @hybrid_property
    def archived(self):
        """Compute the archived status
        """
        try:
            last_move = self._moves.filter(Move.type != MOVE_TYPE_COMMENT)\
                .order_by(Move.moved_on_datetime.desc()).limit(1).one()
            return last_move.type == MOVE_TYPE_ARCHIVED
        except NoResultFound:
            return False

    @property
    def average_rating(self):
        # TODO note should come from database
        return 0

    @hybrid_property
    def name(self):
        return characterentities.decode(self._name)

    @name.setter
    def name(self, name):
        # Drop all html tags
        name_clean = bleach.clean(name, tags=[], strip=True)
        # Strip spaces
        self._name = characterentities.decode(name_clean).strip()

    @name.expression
    def name(cls):
        return cls._name

    @hybrid_property
    def description(self):
        return characterentities.decode(self._description)

    @description.setter
    def description(self, description):
        if description is None:
            description = ''
        # Drop all unallowed html tags
        description_clean = bleach.clean(description, strip=True)
        # Strip spaces
        self._description = characterentities.decode(description_clean).strip()

    @description.expression
    def description(cls):
        return cls._description


@event.listens_for(Geokret, 'init')
def receive_init(target, args, kwargs):
    target.tracking_code = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(6))  # TODO


@event.listens_for(Geokret, 'before_insert')
def before_insert_listener(mapper, connection, target):
    if not target.created_on_datetime:
        target.created_on_datetime = round_microseconds(datetime.utcnow())
    target.updated_on_datetime = target.created_on_datetime


@event.listens_for(Geokret, 'before_update')
def before_update_listener(mapper, connection, target):
    target.updated_on_datetime = round_microseconds(datetime.utcnow())
