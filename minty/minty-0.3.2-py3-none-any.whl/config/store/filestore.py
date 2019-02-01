import os

from .base import ConfigStoreBase


class FileStore(ConfigStoreBase):
    __slots__ = ["base_directory"]

    def __init__(self, directory=None):
        """Initialize connection to filestore

        :param directory: location of configuration files
        :type directory: str
        """

        self.base_directory = directory

    def retrieve(self, name: str = None) -> str:
        """Retrieve configuration from a file

        :param name: base name of the configuration file
        :type name: str
        :return: configuration file contents
        :rtype: str
        """

        super().retrieve(name)

        fullpath = os.path.join(self.base_directory, name + ".conf")

        with self.statsd.get_timer().time("retrieve_time"):
            with open(fullpath, "r", encoding="utf-8") as file:
                content = file.read()

        self.statsd.get_counter().increment("retrieve")

        return content
