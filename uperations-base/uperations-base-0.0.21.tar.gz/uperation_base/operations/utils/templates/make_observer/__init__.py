
from uperations.operation_observer import OperationObserver

class OBSERVER_NAME(OperationObserver):

    def _before_start(self, operation, arg=None):
        return

    def _on_running(self, operation, arg=None):
        return

    def _on_completed(self, operation, arg=None):
        return

    def _on_error(self, error, operation, arg=None):
        return