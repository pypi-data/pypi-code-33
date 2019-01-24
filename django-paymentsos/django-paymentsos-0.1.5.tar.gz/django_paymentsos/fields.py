import ast
import json

from django.db import models


class JSONField(models.TextField):
    def from_db_value(self, value, expression, connection):
        if value is None or value == '':
            return value
        return json.loads(value)

    def to_python(self, value):
        if value is None or value == '':
            return value
        if not isinstance(value, dict):
            value = ast.literal_eval(value)
        return value

    def get_prep_value(self, value):
        if value is None or value == '':
            return value
        if not isinstance(value, dict):
            value = ast.literal_eval(value)
        return json.dumps(value)
