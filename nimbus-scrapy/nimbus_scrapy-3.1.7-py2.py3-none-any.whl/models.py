# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import os
import sys
import logging
import json
from functools import wraps
import scrapy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import ConcreteBase, AbstractConcreteBase, DeferredReflection
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy import Column, String, Integer, DateTime, Text, INTEGER, ColumnDefault
from sqlalchemy import MetaData
from sqlalchemy import text
from sqlalchemy import func
from sqlalchemy.orm import load_only
from nimbus_utils.encoding import smart_text, smart_bytes

from .data import Base

__all__ = ["Base", "BaseModel", "create_table", ]


class BaseModel(AbstractConcreteBase, Base):
    _item = None
    _fields_default_map = {}
    _fields_check = []

    @classmethod
    def save(cls, item=None, **kwargs):
        model = cls()
        model._item = item
        model.setup(**kwargs)
        return model

    @property
    def item(self):
        if self._item is not None:
            return self._item
        self._item = {}
        return self._item

    def get_field_default(self, field):
        d = None
        f = getattr(self, field, None)
        if field in self._fields_default_map:
            d = self._fields_default_map.get(field, None)
        elif f and isinstance(f, Column):
            d = f.default
        return d

    def get_field_value(self, field, **kwargs):
        default = self.get_field_default(field)
        if field in kwargs:
            return kwargs.get(field, default)
        return self.item.get(field, default)

    def check_field_value(self, field, value):
        return smart_text(value)

    def _check_field_value(self, field, value):
        if field in self._fields_check:
            return self.check_field_value(field, value)
        return value

    def get_fields(self, **kwargs):
        _item = self.item
        _fields = list(kwargs.keys())
        if _item and isinstance(_item, scrapy.Item):
            _fields = _fields + list(_item.fields.keys())
        return list(set(_fields))

    def setup(self, **kwargs):
        fields = self.get_fields(**kwargs)
        for f in fields:
            v = self.get_field_value(f, **kwargs)
            if not f.startswith('_') and hasattr(self, f) and v is not None:
                v = self._check_field_value(f, v)
                setattr(self, f, v)


def create_table(engine, model):
    if model and engine and isinstance(model, Base):
        model.metadata.create_all(bind=engine)
    return True

