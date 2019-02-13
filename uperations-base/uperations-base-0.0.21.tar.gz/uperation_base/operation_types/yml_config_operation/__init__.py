import logging
import yaml
from jsonschema import Draft4Validator
from uperations.operation import Operation
from argparse import FileType

from abc import abstractmethod


class YmlConfigOperation(Operation):

    @property
    @abstractmethod
    def _config_schema(self):
        raise NotImplementedError("This operation needs a _config_schema function: "+self.__class__.__name__)

    def _parser(self, main_parser):
        main_parser.add_argument('config', help="Yaml Configuration file", type=FileType('r'))
        return main_parser

    def _before_start(self):
        super(YmlConfigOperation, self)._before_start()
        self.__load_config(self.args.config)
        self.__validate_config()
        return True

    def __validate_config(self):
        v = Draft4Validator(self._config_schema())
        errors = sorted(v.iter_errors(self.config), key=lambda e: e.path)
        if len(errors) > 0:
            for error in errors:
                logging.error("Confguration file: "+error.message)
        return

    def __load_config(self, yml_file_p):
        """
        Transform an opened yaml file in json

        Args:
            yml_file_p:  A pointer to a file opened in read mode

        Return:
            dict: The yaml file in dict format
        """
        self.config = yaml.load(yml_file_p)
        return