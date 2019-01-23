# -*- coding: utf-8 -*-

import datetime
import random

import phpass
from sqlalchemy import Boolean, Column, DateTime, Integer, String, event
from sqlalchemy.dialects.mysql import DOUBLE, INTEGER
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import bleach
import characterentities

from .base import Base


def random_0_23():
    return random.randrange(0, 23)


class User(Base):
    __tablename__ = 'gk-users'

    id = Column(
        'userid',
        Integer,
        primary_key=True,
        key='id',
    )
    _name = Column(
        'user',
        String(80),
        key='name',
        nullable=False,
        unique=True,
    )
    is_admin = Column(
        'is_admin',
        Boolean,
        key='is_admin',
        nullable=True,
        default=False,
    )
    _password = Column(
        'haslo2',
        String(120),
        key='password',
        nullable=False,
    )
    email = Column(
        String(150),
        nullable=False,
        unique=True,
    )
    daily_mails = Column(
        'wysylacmaile',
        Boolean,
        key='daily_news',
        nullable=False,
        default=False,
    )
    ip = Column(
        String(39),
        nullable=True,
        default=None,
    )
    language = Column(
        'lang',
        String(2),
        key='language',
        nullable=False,
        default="",
    )
    latitude = Column(
        'lat',
        DOUBLE(precision=8, scale=5),
        key='latitude',
        nullable=True,
        default=None,
    )
    longitude = Column(
        'lon',
        DOUBLE(precision=8, scale=5),
        key='longitude',
        nullable=True,
        default=None,
    )
    observation_radius = Column(
        'promien',
        INTEGER(unsigned=True),
        key='observation_radius',
        default=0,
    )
    country = Column(
        String(3),
        nullable=True,
        default=None,
    )
    hour = Column(
        'godzina',
        Integer,
        key='hour',
        default=random_0_23,
    )
    statpic_id = Column(
        'statpic',
        Integer,
        key='statpic_id',
        default=1,
    )
    join_datetime = Column(
        'joined',
        DateTime,
        key='join_datetime',
        default=datetime.datetime.utcnow,
    )
    last_mail_datetime = Column(
        'ostatni_mail',
        DateTime,
        nullable=True,
        key='last_mail_datetime',
        default=None,
    )
    last_login_datetime = Column(
        'ostatni_login',
        DateTime,
        nullable=True,
        key='last_login_datetime',
        default=None,
    )
    last_update_datetime = Column(
        'timestamp',
        DateTime,
        key='last_update_datetime',
        default=datetime.datetime.utcnow,
    )
    secid = Column(
        String(128),
    )

    news = relationship(
        'News',
        backref="author",
        cascade="all,delete",
    )
    news_comments = relationship(
        'NewsComment',
        backref="author",
        cascade="all,delete",
    )
    news_subscriptions = relationship(
        'NewsSubscription',
        backref="user",
        cascade="all,delete",
    )

    @hybrid_property
    def password(self):
        """
        Hybrid property for password
        :return:
        """
        return self._password

    @password.setter
    def password(self, password):
        """
        Setter for _password, saves hashed password, salt and reset_password string
        :param password:
        :return:
        """
        t_hasher = phpass.PasswordHash(11, False)
        self._password = t_hasher.hash_password(
            password.encode('utf-8') + "DDD"  # app.config['PASSWORD_HASH_SALT']
        )

    @password.expression
    def password(cls):
        return cls._password

    @hybrid_property
    def name(self):
        return characterentities.decode(self._name)

    @name.setter
    def name(self, name):
        name_clean = bleach.clean(name, tags=[], strip=True)
        self._name = characterentities.decode(name_clean).strip()

    @name.expression
    def name(cls):
        return cls._name


@event.listens_for(User, 'init')
def receive_init(target, args, kwargs):
    target.secid = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(84))  # TODO
    # target.ip = request.remote_addr
