from santa.parser import YamlLoader, YamlLoaderBase


class ExtractorBase(YamlLoaderBase):
    type_name = "extractor"
    registry = {}


class Extractor(YamlLoader, metaclass=ExtractorBase):
    __abstract__ = True

    async def __call__(self, response, ctx):
        raise NotImplementedError()


extractor_factory = Extractor._factory
