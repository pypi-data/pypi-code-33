# -*- coding: utf-8 -*-

import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import bleach
import characterentities

from .base import Base


class Badge(Base):
    __tablename__ = 'gk-badges-collection'

    id = Column(
        'id',
        Integer,
        primary_key=True,
        key='id',
    )

    _name = Column(
        'name',
        String(80),
        key='name',
        nullable=False,
        unique=True,
    )

    _description = Column(
        'description',
        String(128),
        key='description',
        nullable=True,
    )

    filename = Column(
        'filename',
        String(32),
        key='filename',
        nullable=False,
    )

    created_on_datetime = Column(
        'date',
        DateTime,
        key='created_on_datetime',
        nullable=False,
        default=datetime.datetime.utcnow,
    )

    author_id = Column(
        'author_id',
        Integer,
        ForeignKey('gk-users.id'),
        key='author_id',
        nullable=False,
    )

    author = relationship(
        "User",
        foreign_keys=[author_id],
        backref="created_badges"
    )

    @hybrid_property
    def name(self):
        return characterentities.decode(self._name)

    @name.setter
    def name(self, name):
        name_clean = bleach.clean(name, strip=True)
        self._name = characterentities.decode(name_clean).strip()

    @name.expression
    def name(cls):
        return cls._name

    @hybrid_property
    def description(self):
        if self._description is None:
            return u''
        return characterentities.decode(self._description)

    @description.setter
    def description(self, description):
        if description is None:
            return u''
        description_clean = bleach.clean(description, strip=True)
        self._description = characterentities.decode(description_clean).replace('\x00', '').strip()

    @description.expression
    def description(cls):
        return cls._description

    @hybrid_property
    def upload_url(self):
        # Todo send info to other daemon -> redis?
        from app.views.minio import storage
        res = storage.connection.presigned_put_object(
            'badges-incoming', self.filename)  # , expires=timedelta(minutes=5))
        return res
        # return uuid.uuid4().hex


@event.listens_for(Badge, 'init')
def receive_init(target, args, kwargs):
    target.filename = uuid.uuid4().hex


if __name__ == '__main__':
    # Check
    badge = Badge()
