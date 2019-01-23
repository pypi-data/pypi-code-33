# pylint: disable=too-few-public-methods,invalid-name
import json
from cerberus import Validator
from reliabilly.components.logger import Logger
from reliabilly.settings import Constants


class Field:
    def __init__(self, var_type, **kwargs):
        self.type = var_type
        self.schema = {}
        for key, value in kwargs.items():
            self.schema[key] = value


SchemaTypeMappings = {
    "bool": "boolean",
    "bytes": "binary",
    "datetime.date": "date",
    "datetime.datetime": "datetime",
    "dict": "dict",
    "float": "float",
    "int": "integer",
    "list": "list",
    "set": "set",
    "str": "string"
}


class BaseModel:
    logger = Logger()
    id: str  # pylint: disable=invalid-name

    def __init__(self, dictionary=None):
        if dictionary:
            vars(self).update(dictionary)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.to_json(self)

    # pylint: disable=inconsistent-return-statements
    @staticmethod
    def safe_set_attribute(attribute):
        if attribute:
            return attribute

    def get_attribute(self, attribute_name):
        return self.__dict__.get(attribute_name, Constants.EMPTY)

    @staticmethod
    def from_json(json_string):
        return json.loads(json_string, object_hook=BaseModel)

    def get_json(self):
        return BaseModel.to_json(self)

    @staticmethod
    def to_json(model):
        return json.dumps(model.__dict__, default=str)

    def validate(self, model=None, schema=None):
        if schema is None:
            schema = self.to_schema()
            if not schema:
                return True
        validator = Validator(schema)
        model_data = self.__dict__
        if model:
            model_data = model
        result = validator.validate(model_data)
        self.logger.info(f'Validation errors: {validator.errors}')
        return result

    def to_schema(self):
        schema = {}
        # pylint: disable=no-member
        functions = self.__annotations__
        for key, value in functions.items():
            # pylint: disable=unidiomatic-typecheck
            if type(value) is not Field:
                return False
            schema[key] = {'type': SchemaTypeMappings[value.type.__name__],}
            schema[key].update(value.schema)
        return schema
