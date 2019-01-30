import json
from datetime import datetime
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import class_mapper, MapperExtension
from .app import db
from .exception import CoreException
from flask import g


def flush():
    try:
        db.session.flush()
    except DatabaseError:
        db.session.rollback()
        raise


class Entity(MapperExtension):
    __json_public__ = None
    __json_hidden__ = None
    __json_modifiers__ = None
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    created_by = db.Column(db.String(64), nullable=False)

    updated_at = db.Column(db.DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)

    updated_by = db.Column(db.String(64), nullable=False)

    def before_insert(self, mapper, connection, instance):
        """ Make sure the audit fields are set correctly  """

        if g.username is not None:
            instance.created_by = g.username
            instance.updated_by = g.username
        else:
            instance.created_by = 'system'
            instance.updated_by = 'system'

        instance.updated_at = datetime.now()
        instance.created_at = datetime.now()

    def before_update(self, mapper, connection, instance):
        """ Make sure when we update this record the created fields stay unchanged!  """
        instance.created_at = instance.created_at
        instance.created_by = instance.created_by

    def __init__(self, obj=None):
        """
        :rtype: object
        """
        self.__mapper__ = None
        if obj is not None:
            self.from_dict(self, obj)
        pass

    @staticmethod
    def from_dict(self, obj):
        for k, v in obj.items():
            if isinstance(v, dict):
                setattr(self, k, Entity(v))
            else:
                setattr(self, k, v)

    def save(self):
        db.session.add(self)
        flush()

    def delete(self):
        db.session.delete(self)
        flush()

    def update(self, obj):
        if obj is None:
            raise CoreException('object cannot be none')
        if not isinstance(obj, dict):
            raise CoreException('object must be instances of dict')
        for attr, value in obj.items():
            print('{}:{}'.format(attr, value))
            setattr(self, attr, value)
        return self.save()

    def get_field_names(self):
        for p in class_mapper(self.__class__).iterate_properties:
            yield p.key

    def to_dict(self):
        field_names = self.get_field_names()
        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        modifiers = self.__json_modifiers__ or dict()
        rv = dict()
        for key in public:
            value = getattr(self, key)
            if isinstance(value, list):
                child_list = []
                for v in value:
                    child = {}
                    for k in class_mapper(v.__class__).iterate_properties:
                        child[k.key] = getattr(v, k.key)
                    child_list.append(child)
                if len(child_list) > 0:
                    rv.update({key: child_list})
                continue

            if issubclass(type(value), db.Model):
                child = {}
                for k in class_mapper(value.__class__).iterate_properties:
                    child[k.key] = getattr(value, k.key)
                    pass
                rv.update({key: child})
                continue

            if value is not None:
                rv[key] = value
        for key, modifier in modifiers.items():
            value = getattr(self, key)
            rv[key] = modifier(value, self)
        for key in hidden:
            if '.' in key:
                split = key.split('.')
                if isinstance(rv[split[0]], dict):
                    for k in split[1:]:
                        rv[split[0]].pop(k, None)
            else:
                rv.pop(key, None)
        return rv

    def to_json(self):
        return json.dump(self.to_dict)
