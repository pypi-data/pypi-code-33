
import inspect
import json
import logging

from colibris import schemas

from testmyesp.instructions.exceptions import NoSuchInstruction

from . import get_instruction_class


class BaseInstruction:
    _SCHEMA_FIELD_MAPPING = {
        str: schemas.fields.String,
        int: schemas.fields.Integer,
        bool: schemas.fields.Boolean
    }

    NAME = None

    def __init__(self):
        self.logger = None
        self.serial = None
        self.test_case = None

    def __str__(self):
        return 'instruction {}'.format(repr(self))

    def __repr__(self):
        schema_class = self.get_schema_class()
        schema = schema_class()

        param_names = [f for f in schema.fields]
        param_values = self.get_params()
        params = ((k, self._get_param_repr(param_values[k])) for k in param_names if k in param_values)
        params = sorted(params, key=lambda p: p[0])
        params = ('{}={}'.format(k, v) for k, v in params)
        params_str = ', '.join(params)

        return '{}({})'.format(self.__class__.__name__, params_str)

    @staticmethod
    def _get_param_repr(param):
        if isinstance(param, (int, float, str)):
            return json.dumps(param)

        elif param is None:
            return 'None'

        else:
            return '<...>'

    def set_logger(self, test_case_logger):
        self.logger = logging.getLogger(test_case_logger.name + '.' + self.__class__.__name__)

    def set_serial(self, serial):
        self.serial = serial

    def set_test_case(self, test_case):
        self.test_case = test_case

    def get_params(self):
        # by default, params are all public properties
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith('_') and not inspect.ismethod(v)}

    def execute(self):
        raise NotImplementedError

    def tear_down_test_case(self):
        pass

    def tear_down_job(self):
        pass

    @classmethod
    def get_schema_class(cls):
        if cls.Schema is BaseInstruction.Schema or cls.Schema is None:
            cls.Schema = cls._infer_schema()

        return cls.Schema

    @classmethod
    def _infer_schema(cls):
        s = inspect.signature(cls.__init__)
        param_types = {p.name: p.annotation for p in s.parameters.values()
                       if p.annotation is not inspect.Parameter.empty}
        param_required = {p.name: p.default is inspect.Parameter.empty for p in s.parameters.values()}

        fields = {p: cls._SCHEMA_FIELD_MAPPING[t](required=param_required.get(p, True)) for p, t in param_types.items()
                  if t in cls._SCHEMA_FIELD_MAPPING}

        return type('Schema', (schemas.Schema,), fields)

    @staticmethod
    def from_dict(d):
        # TODO add version to dict

        name = d['name']
        cls = get_instruction_class(name)
        if cls is None:
            raise NoSuchInstruction(name)

        return cls(**d['params'])

    class Schema(schemas.Schema):
        pass
