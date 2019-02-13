import logging
from jsonschema import Draft4Validator
from uperations.operation import Operation
from argparse import FileType
from abc import abstractmethod
import json


class JsonOperation(Operation):

    @property
    @abstractmethod
    def _config_schema(self):
        raise NotImplementedError("This operation needs a _config_schema function: "+self.__class__.__name__)

    def _parser(self, main_parser):
        main_parser.add_argument('json', help="Json input file", type=FileType('r'))
        return main_parser

    def _before_start(self):
        super(JsonOperation, self)._before_start()
        self.json = json.load(self.args.json)
        return True

    def __validate_json(self):
        v = Draft4Validator(self._config_schema())
        errors = sorted(v.iter_errors(self.json), key=lambda e: e.path)
        if len(errors) > 0:
            for error in errors:
                logging.error("Json file: "+error.message)
        return