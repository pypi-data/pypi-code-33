# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship

import bleach
import characterentities

from .base import Base
from .utilities.date import round_microseconds


class Move(Base):
    __tablename__ = 'gk-ruchy'

    id = Column(
        'ruch_id',
        Integer,
        primary_key=True,
        key='id'
    )

    geokret_id = Column(
        'id',
        Integer,
        ForeignKey('gk-geokrety.id', name='fk_geokret_moved'),
        key='geokret_id',
        nullable=False,
        default=None
    )
    geokret = relationship(
        "Geokret",
        foreign_keys=[geokret_id],
        backref=backref("moves", order_by="-Move.moved_on_datetime")
    )

    latitude = Column(
        'lat',
        DOUBLE(precision=8, scale=5),
        key='latitude',
        nullable=True,
        default=None
    )

    longitude = Column(
        'lon',
        DOUBLE(precision=8, scale=5),
        key='longitude',
        nullable=True,
        default=None
    )

    altitude = Column(
        'alt',
        Integer,
        key='altitude',
        nullable=True,
        default=None,
    )

    country = Column(
        'country',
        String(3),
        key='country',
        nullable=True,
        default=None,
    )

    distance = Column(
        'droga',
        Integer,
        key='distance',
        nullable=False,
        default=0
    )

    waypoint = Column(
        'waypoint',
        String(10),
        key='waypoint',
        nullable=False,
        default=''
    )

    _comment = Column(
        'koment',
        String(5120),
        key='comment',
        nullable=False,
        default=''
    )

    pictures_count = Column(
        'zdjecia',
        Integer,
        key='pictures_count',
        nullable=False,
        default=0
    )

    comments_count = Column(
        'komentarze',
        Integer,
        key='comments_count',
        nullable=False,
        default=0
    )

    type = Column(
        'logtype',
        Enum('0', '1', '2', '3', '4', '5'),
        key='type',
        nullable=False,
    )

    author_id = Column(
        'user',
        Integer,
        ForeignKey('gk-users.id'),
        key='author_id',
        nullable=False,
        default=None,
    )
    author = relationship("User", foreign_keys=[author_id], backref="moves")

    username = Column(
        'username',
        String(20),
        key='username',
        nullable=False,
        default=''
    )

    # This is used to compute the missing status
    _move_comments = relationship(
        'MoveComment',
        foreign_keys="MoveComment.move_id",
        lazy="dynamic",
    )

    moved_on_datetime = Column(
        'data',
        DateTime,
        key='moved_on_datetime',
        nullable=False,
        default=datetime.utcnow,
    )

    created_on_datetime = Column(
        'data_dodania',
        DateTime,
        key='created_on_datetime',
        nullable=False,
        default=datetime.utcnow,
    )

    updated_on_datetime = Column(
        'timestamp',
        DateTime,
        key='updated_on_datetime',
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    _application_name = Column(
        'app',
        String(16),
        key='application_name',
        nullable=True
    )

    _application_version = Column(
        'app_ver',
        String(16),
        key='application_version',
        nullable=True
    )

    @hybrid_property
    def comment(self):
        return characterentities.decode(self._comment)

    @comment.setter
    def comment(self, comment):
        comment_clean = bleach.clean(comment, strip=True)
        self._comment = characterentities.decode(comment_clean).strip()

    @comment.expression
    def comment(cls):
        return cls._comment

    @hybrid_property
    def application_version(self):
        if self._application_version is None:
            return None
        return characterentities.decode(self._application_version)

    @application_version.setter
    def application_version(self, application_version):
        if application_version is None:
            self._application_version = None
        else:
            application_version_clean = bleach.clean(application_version, tags=[], strip=True)
            self._application_version = characterentities.decode(application_version_clean).strip()

    @application_version.expression
    def application_version(cls):
        return cls._application_version

    @hybrid_property
    def application_name(self):
        if self._application_name is None:
            return None
        return characterentities.decode(self._application_name)

    @application_name.setter
    def application_name(self, application_name):
        if application_name is None:
            self._application_name = None
        else:
            application_name_clean = bleach.clean(application_name, tags=[], strip=True)
            self._application_name = characterentities.decode(application_name_clean).strip()

    @application_name.expression
    def application_name(cls):
        return cls._application_name

    @hybrid_property
    def _moved_on_datetime(self):
        if isinstance(self.moved_on_datetime, str):
            self.moved_on_datetime = datetime.strptime(self.moved_on_datetime, "%Y-%m-%dT%H:%M:%S")
        return round_microseconds(self.moved_on_datetime)
