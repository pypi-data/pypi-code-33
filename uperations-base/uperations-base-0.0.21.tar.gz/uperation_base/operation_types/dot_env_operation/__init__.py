from uperations.operation import Operation
from argparse import FileType
from dotenv import load_dotenv

class DotEnvOperation(Operation):

    def _parser(self, main_parser):
        main_parser.add_argument('--env', help=".env file path", type=str, default='.env')
        return main_parser

    def _before_start(self):
        super(DotEnvOperation, self)._before_start()
        load_dotenv(self.args.env, verbose=True)
        return True

    def _on_running(self):
        super(DotEnvOperation, self)._on_running()
        return True

    def _on_error(self, exception):
        super(DotEnvOperation, self)._on_error(exception)
        return True

    def _on_completed(self):
        super(DotEnvOperation, self)._on_completed()
        return True