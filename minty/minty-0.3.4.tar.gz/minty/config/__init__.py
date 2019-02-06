from .parser.base import ConfigParserBase
from .store.base import ConfigStoreBase


class Configuration:
    __slots__ = ["parser", "store"]

    def __init__(self, store: ConfigStoreBase, parser: ConfigParserBase):
        """Initialize a configuration object

        :param store: instance of the ConfigStoreBase to use
        :type store: ConfigStoreBase
        :param parser: instance of the ConfigParserBase module to use
        :type parser: ConfigParserBase
        """

        self.parser = parser
        self.store = store

    def get(self, name: str) -> dict:
        """Get the named configuration from the configured store

        :param name: name of the environment to retrieve configuration for
        :param name: str, optional
        :return: the configuration
        :rtype: dict
        """

        raw_configuration = self.store.retrieve(name=name)
        configuration = self.parser.parse(content=raw_configuration)

        return configuration
