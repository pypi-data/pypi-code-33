from santa.parser import YamlLoader, YamlLoaderBase


class ValidatorBase(YamlLoaderBase):
    type_name = "validator"
    registry = {}


class Validator(YamlLoader, metaclass=ValidatorBase):
    __abstract__ = True

    async def __call__(self, response, ctx):
        raise NotImplementedError()


validator_factory = Validator._factory


class ValidationError(Exception):
    pass
