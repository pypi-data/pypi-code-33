"""Storage for errors or unfound indexes. Reset on each run"""

from headerindexer.data_factory._z_data_docs import ErrorsDocs, ErrorsFactoryDocs


class Errors(ErrorsDocs):

    def __init__(self):
        self.reset()

    def reset(self):

        self.__setattr__('stderr', '\n')

        self.nonindexed.clear()

        self.duplicates.clear()


class ErrorsFactory(ErrorsFactoryDocs):

    @staticmethod
    def _return_errors_obj():
        return Errors()

    def new_errors_obj(self):
        errors_to_return = self._return_errors_obj()
        return errors_to_return
