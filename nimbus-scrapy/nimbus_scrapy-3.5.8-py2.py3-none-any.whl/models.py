# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import os
import sys
import logging
import json
import inspect
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
    EXCLUDE_FIELDS = ["type", "metadata", ]

    _item = None
    _fields = None
    _initial_data = {}
    _cleaned_data = {}

    field_default_mapping = {}
    field_item_mapping = {}

    @classmethod
    def save(cls, item=None, **kwargs):
        model = cls()
        model._item = item
        model.setup(**kwargs)
        return model

    def setup(self, **kwargs):
        self._initial_item_data(**kwargs)
        self._cleaned_data = {}
        self._collect_fields()
        self._clean_fields()
        self._save_fields()

    def _initial_item_data(self, **kwargs):
        self._initial_data = dict(self._item)
        self._initial_data.update(kwargs)

    def _collect_fields(self):
        self._fields = [name for name, _ in inspect.getmembers(self, predicate=self._is_valid_field)
                        if not name.startswith("_") and name not in self.EXCLUDE_FIELDS]

    def _clean_fields(self):
        for field in self._fields:
            value = self._get_initial_for_field(field)
            self._cleaned_data[field] = value
            if hasattr(self, 'clean_%s' % field):
                self._cleaned_data[field] = getattr(self, 'clean_%s' % field)(value)

    def _save_fields(self):
        for field in self._fields:
            value = self._cleaned_data.get(field, None)
            if value is not None and hasattr(self, field):
                setattr(self, field, value)

    def _is_valid_field(self, value):
        if value is None or isinstance(value, Column):
            return True
        return False

    def _get_initial_for_field(self, field):
        f = getattr(self, field, None)
        _item_field = self.field_item_mapping.get(field, field)
        value = self._initial_data.get(_item_field, None)
        if value is None:
            if field in self.field_default_mapping:
                value = self.field_default_mapping.get(field, None)
            elif f and isinstance(f, Column):
                value = f.default
        return value
    

def create_table(engine, model):
    if model and engine and isinstance(model, Base):
        model.metadata.create_all(bind=engine)
    return True

