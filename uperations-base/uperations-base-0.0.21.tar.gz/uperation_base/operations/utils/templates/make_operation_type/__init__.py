from uperations.operation import Operation

class OPERATIONTYPE(Operation):

    def _parser(self, main_parser):
        super(OPERATIONTYPE, self)._parser(main_parser)
        #main_parser.add_argument('first_argument', help="Argparse argument example")
        return main_parser

    def _before_start(self):
        super(OPERATIONTYPE, self)._before_start()
        #print(self.args.first_argument)
        return True

    def _on_running(self):
        super(OPERATIONTYPE, self)._on_running()
        return True

    def _on_error(self, exception):
        super(OPERATIONTYPE, self)._on_error(exception)
        return True

    def _on_completed(self):
        super(OPERATIONTYPE, self)._on_completed()
        return True