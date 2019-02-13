

from uperations.operation import Operation
from ..utils import create_operation_type
from uperations.kernel import Kernel


class MakeOperationType(Operation):

    @staticmethod
    def name():
        return "make_operationtype"

    @staticmethod
    def description():
        return "Create a new operation type"

    def _parser(self, main_parser):
        main_parser.add_argument('library', help="Name of the library to add the operation type")
        main_parser.add_argument('type', help="Name of the operation type")
        return

    def _run(self):
        create_operation_type(Kernel.get_instance().find_library(self.args.library),self.args.type)
        return True


    @staticmethod
    def to_camel_case(snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])