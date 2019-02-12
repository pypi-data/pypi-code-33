from django.db import models
import json

from django.utils.encoding import (
    force_bytes, force_text, python_2_unicode_compatible, smart_text,
)
from django.utils import six
from django.conf import settings
from ..model.Images import ImageModel

import ast


class ImageSetField(models.TextField):
    # __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ImageSetField, self).__init__(*args, **kwargs)

    @property
    def urls(self):
        return ['name',"page"]

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if isinstance(value,str):
            print('str --- ')

        if isinstance(value,list):
            print('list --- ')

        if isinstance(value,object):
            print('obj --- ')

        print("++++++OOO",value)
        if value is None:
            return value

        return str(value)  # use str(value) in Python 3

