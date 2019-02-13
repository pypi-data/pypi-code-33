
from ...operation_types.log_operation import LogOperation

class Test(LogOperation):

    @staticmethod
    def name():
        return "Test"

    @staticmethod
    def description():
        return "Test has not been documented yet."

    def _parser(self, main_parser):
        #main_parser.add_argument('first_argument', help="Argparse argument example")
        return

    def _run(self):
        print("ok")
        return