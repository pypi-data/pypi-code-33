
from uperations.operation import Operation
import kernel
from libraries.base.operations.utils import create_event

class MakeEvent(Operation):

    @staticmethod
    def name():
        return "make_event"

    @staticmethod
    def description():
        return "Create an event for an existing operation"

    def _parser(self, main_parser):
        main_parser.add_argument('library', help="Name of the library")
        main_parser.add_argument('operation', help="Name of the operation")
        main_parser.add_argument('event', help="Name of the event")
        return

    def is_publishable(self):
        return True

    def _run(self):
        operation = kernel.find_operation(self.args.library, self.args.operation)
        create_event(operation,self.args.event)
        return