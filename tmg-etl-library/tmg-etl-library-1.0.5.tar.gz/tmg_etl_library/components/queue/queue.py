from abc import abstractmethod
from tmg_etl_library.components.component import Component


class Local(Component):
    def __init__(self, log):
        super().__init__(log)

    @abstractmethod
    def publish_messages(self):
        pass

    @abstractmethod
    def consume_messages(self):
        pass
