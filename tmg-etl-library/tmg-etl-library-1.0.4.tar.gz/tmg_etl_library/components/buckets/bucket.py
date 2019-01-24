from abc import abstractmethod
from tmg_etl_library.components.component import Component


class Bucket(Component):

    def __init__(self, log):
        super().__init__(log)

    @abstractmethod
    def upload_files(self):
        pass

    @abstractmethod
    def download_files(self):
        pass

    @abstractmethod
    def list_files(self):
        pass

    @abstractmethod
    def delete_files(self):
        pass

