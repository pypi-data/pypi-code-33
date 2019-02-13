from uperations.operation import Operation
import logging

class LogOperation(Operation):

    def _parser(self, main_parser):
        super(LogOperation, self)._parser(main_parser)
        main_parser.add_argument('--log',dest='LOG_FILE', help="Log file", required=False)
        main_parser.add_argument('--log-level',dest='LOG_LEVEL', help="Log level", required=False, choices=['info','debug'])
        return main_parser

    def _before_start(self):
        super(LogOperation, self)._before_start()
        print(getattr(logging, self.args.LOG_LEVEL.upper()))
        #print(self.args.first_argument)
        return True

    def _on_running(self):
        super(LogOperation, self)._on_running()
        return True

    def _on_error(self, exception):
        super(LogOperation, self)._on_error(exception)
        return True

    def _on_completed(self):
        super(LogOperation, self)._on_completed()
        return True