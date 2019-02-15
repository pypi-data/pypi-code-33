class MyMongoClient:
    _config = None
    _logger = None

    def __init__(self, config, logger):
        self._config = config
        self._logger = logger

    def start(self):
        pass

    def stop(self):
        pass

    def write_shadow(self, document):
        pass
