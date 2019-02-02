from abc import ABC, abstractmethod


class Assistant(ABC):

    @abstractmethod
    def message(self, parameters):
        pass

    @abstractmethod
    def information(self, parameters):
        pass
