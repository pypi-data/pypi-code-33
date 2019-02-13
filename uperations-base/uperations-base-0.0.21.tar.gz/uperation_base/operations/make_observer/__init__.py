
from uperations.operation import Operation
from ..utils import create_observer

class MakeObserver(Operation):

    @staticmethod
    def name():
        return "make_observer"

    @staticmethod
    def description():
        return "Create an observer"

    def _parser(self, main_parser):
        main_parser.add_argument('observer', help="Observer name - No special characters")
        return

    def _run(self):
        create_observer(self.args.observer)
        return
