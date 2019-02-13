
from uperations.library import Library

class LIBRARYNAME(Library):

    @staticmethod
    def name():
        return "LIBRARYNAME"

    @staticmethod
    def description():
        return "Not description provided"

    def _init_operations(self):
        self._operations = {
            # operation_command: OperationClass(self)
        }
        return

    def operations(self):
        return self._operations