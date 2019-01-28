from drongo.utils import dict2


class Module(object):
    __default_config__ = {}

    def __init__(self, app, **kwargs):
        self.app = app
        self.config = dict2()
        self.config.update(self.__default_config__)
        self.config.update(kwargs)

        self.init(self.config)
