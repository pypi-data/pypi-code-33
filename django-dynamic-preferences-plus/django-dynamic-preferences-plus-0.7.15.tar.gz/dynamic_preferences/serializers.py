# !/usr/bin/env python
# encoding:UTF-8

import os
from six import string_types
from django.conf import settings
from django.core.files.storage import default_storage
from fields import FieldUpfile
from django.template import defaultfilters
from dynamic_preferences.settings import preferences_settings
from django.utils import timezone


class SerializationError(Exception):
    pass


class BaseSerializer(object):
    """
    A serializer take a Python variable and returns a string that can be stored safely in database
    """
    exception = SerializationError

    @classmethod
    def serialize(cls, value, **kwargs):
        """
        Return a string from a Python var
        """
        raise NotImplementedError

    @classmethod
    def deserialize(cls, value, **kwargs):
        """
            Convert a python string to a var
        """
        raise NotImplementedError


class BooleanSerializer(BaseSerializer):
    true = (
        "True",
        "true",
        "TRUE",
        "1",
        "YES",
        "Yes",
        "yes",
    )

    false = (
        "False",
        "false",
        "FALSE",
        "0",
        "No",
        "no",
        "NO",
    )

    @classmethod
    def serialize(cls, value, **kwargs):
        if value:
            return True
        else:
            return False

    @classmethod
    def deserialize(cls, value, **kwargs):
        if value in cls.true:
            return True
        elif value in cls.false:
            return False
        else:
            raise cls.exception("Value {0} can't be deserialized to a Boolean".format(value))


class IntSerializer(BaseSerializer):
    @classmethod
    def serialize(cls, value, **kwargs):
        if not isinstance(value, int):
            raise cls.exception('IntSerializer can only serialize int values')

        return value.__str__()

    @classmethod
    def deserialize(cls, value, **kwargs):
        try:
            return int(value)
        except:
            raise cls.exception("Value {0} cannot be converted to int")


class StringSerializer(BaseSerializer):
    @classmethod
    def serialize(cls, value, **kwargs):
        if not isinstance(value, string_types):
            raise cls.exception("Cannot serialize, value {0} is not a string".format(value))
        if kwargs.get("escape_html", False):
            return defaultfilters.force_escape(value.encode('utf-8'))
        else:
            return value.encode('utf-8')

    @classmethod
    def deserialize(cls, value, **kwargs):
        """String deserialisation just return the value as a string"""
        try:
            return str(value.encode('utf-8'))
        except:
            raise cls.exception("Cannot deserialize value {0} tostring".format(value))


class UnsetValue(object):
    pass


UNSET = UnsetValue()


class FileSerializer(BaseSerializer):
    @classmethod
    def serialize(cls, value, **kwargs):
        """
        Return a string from a Python var
        """
        return cls.to_db(value, **kwargs)

    @classmethod
    def deserialize(cls, value, **kwargs):
        """
            Convert a python string to a var
        """
        return cls.to_python(value, **kwargs)

    @classmethod
    def clean_to_db_value(cls, value):
        return value

    @staticmethod
    def handle_uploaded_file(f, path):
        # create folders for upload_to or app dir if necessary
        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            if not os.path.isdir(os.path.dirname(path)):
                raise

        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    @staticmethod
    def append_suffix(filename):
        # add random suffix to avoid browser cache
        name, ext = os.path.splitext(filename)
        return "{name}_{suffix}{ext}".format(name=name, suffix=timezone.now().strftime('%Y%m%d%H%M%S%f')[-4:], ext=ext)

    @classmethod
    def to_db(cls, dfile, **kwargs):
        # to_db is passed a file object from forms.FileField
        if not settings.MEDIA_ROOT:
            raise cls.exception("You need to set MEDIA_ROOT in your settings.py")
        try:
            dfile.name = cls.append_suffix(dfile.name)
            path = os.path.join(settings.MEDIA_ROOT, preferences_settings.FILE_PREFERENCE_REL_UPLOAD_DIR,
                                dfile.name)
            cls.handle_uploaded_file(dfile, path)
        except AttributeError:
            return ''
        if kwargs.get('delete_filename', None):
            # delete previous file
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, preferences_settings.FILE_PREFERENCE_REL_UPLOAD_DIR,
                                       kwargs.get('delete_filename')))
            except OSError:
                pass
        return dfile.name

    @classmethod
    def to_python(cls, value, **kwargs):

        # https://yuji.wordpress.com/2013/01/30/django-form-field-in-initial-data-requires-a-fieldfile-instance/
        # TODO: Understand this FieldFile better and maybe remove the FakeField workaround
        class FakeField(object):
            storage = default_storage

        filename = value
        if not settings.MEDIA_ROOT:
            raise cls.exception("You need to set MEDIA_ROOT in your settings.py")

        path = os.path.join(settings.MEDIA_ROOT, preferences_settings.FILE_PREFERENCE_REL_UPLOAD_DIR, filename)

        if os.path.isfile(path):

            fieldfile = FieldUpfile(None, FakeField, filename)
            return fieldfile
        else:
            #return None
            fieldfile = FieldUpfile(None, FakeField, filename)
            return fieldfile

