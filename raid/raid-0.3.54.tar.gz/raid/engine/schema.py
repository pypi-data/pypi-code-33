# -*- coding: utf-8 -*-

"""
A schema is something used by a trainer to define which parameters
can be adjusted by the engine. For clarity, you must define each field,
its type, and its value ranges.
"""

import json
from enum import Enum
from typing import Dict

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class FieldType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"


class Field:
    def __init__(
            self,
            name: str,
            field_type: FieldType = FieldType.INT,
            default=None,
            field_range: tuple = None
    ):
        self.name: str = name
        self.field_type: FieldType = field_type
        self.default = default
        self.field_range: tuple = field_range


class Schema:
    def __init__(self):
        self.fields: Dict[str, Field] = {}

    def add_field(
            self,
            name: str,
            field_type: FieldType = FieldType.INT,
            default=None,
            field_range: tuple = None
    ):
        field = Field(name, field_type, default, field_range)
        self.fields[name] = field

    def generate_template(self, path: str):
        """ Generate a JSON template as the configuration for this schema. """
        template_data = {f.name: f.default for _, f in self.fields.items()}
        with open(path, "w") as f:
            json.dump(template_data, f, indent=2)

    def encode(self) -> dict:
        """ Return a dictionary that describes this schema. """
        data = {f.name: {
            "field_type": f.field_type.value,
            "default": f.default,
            "range": list(f.field_range)

        } for _, f in self.fields.items()}
        return data

    def encode_to_file(self, path: str):
        """ Write this schema to disk as a JSON file. """
        with open(path, "w") as f:
            json.dump(self.encode(), f, indent=2)

