
from ...operation_types.yml_config_operation import YmlConfigOperation
import json

class Yamltojson(YmlConfigOperation):

    @staticmethod
    def name():
        return "Yamltojson"

    @staticmethod
    def description():
        return "Display a yaml file as json"

    def _config_schema(self):
        return {}

    def _parser(self, main_parser):
        return

    def _run(self):
        print(json.dumps(self.config))
        return True