

from uperations.library import Library
from .operations.make_library import Makelibrary
from .operations.make_operation import MakeOperation
from .operations.make_operationtype import MakeOperationType
from .operations.list_operation import Listoperation
from .operations.yaml_to_json import Yamltojson
from .operations.publish import Publish
from .operations.command import Command
from .operations.dockerfile import Dockerfile
from .operations.make_observer import MakeObserver
from .operations.test import Test

class Base(Library):

    @staticmethod
    def name():
        return "base"

    @staticmethod
    def description():
        return "General operations"

    def _init_operations(self):
        self._operations = {
            'make:library': Makelibrary(self),
            'make:operation': MakeOperation(self),
            'make:operation:type': MakeOperationType(self),
            'make:observer': MakeObserver(self),
            'list:operations': Listoperation(self),
            'yaml_to_json': Yamltojson(self),
            'publish': Publish(self),
            'command': Command(self),
            'dockerfile': Dockerfile(self),
            'test': Test(self)
        }
        return

    def operations(self):
        return self._operations