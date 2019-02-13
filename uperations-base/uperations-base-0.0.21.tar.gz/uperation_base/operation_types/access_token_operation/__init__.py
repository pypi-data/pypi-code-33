from uperations.operation import Operation
import os

class AccessTokenOperation(Operation):

    def _parser(self, main_parser):
        super(AccessTokenOperation, self)._parser(main_parser)
        main_parser.add_argument('--access-token', dest="access_token", default=os.environ.get('ACCESSTOKEN', None),help="Access token to use", required=True)
        return main_parser

    def _before_start(self):
        super(AccessTokenOperation, self)._before_start()
        return self._validate_token()

    def _on_running(self):
        super(AccessTokenOperation, self)._on_running()
        return True

    def _on_error(self, exception):
        super(AccessTokenOperation, self)._on_error(exception)
        return True

    def _on_completed(self):
        super(AccessTokenOperation, self)._on_completed()
        return True

    def _validate_token(self):
        return True