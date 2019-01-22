from abc import abstractmethod
from tmg_etl_library.components.component import Component


class Local(Component):
    def __init__(self, log):
        super().__init__(log)

    @abstractmethod
    def read_file(self):
        pass

    @abstractmethod
    def delete_file(self):
        pass

    @abstractmethod
    def insert_data(self):
        pass
