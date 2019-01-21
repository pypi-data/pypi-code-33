from santa.parser import YamlLoader, YamlLoaderBase


class ContextProcessorBase(YamlLoaderBase):
    loader_type = "context_processor"
    registry = {}


class ContextProcessor(YamlLoader, metaclass=ContextProcessorBase):
    __abstract__ = True

    async def __call__(self, response, ctx):
        raise NotImplementedError()


context_processor_factory = ContextProcessor._factory
