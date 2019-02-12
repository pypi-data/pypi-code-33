from abc import ABC
from os import environ

from .drivers import Yaml, Json


class BaseLoader(ABC):
    @classmethod
    def isdisabled(cls, disabled):
        return cls.__name__ in disabled

    @classmethod
    def isenabled(cls, enabled):
        if not enabled:
            return True
        return cls.__name__ in enabled

    @classmethod
    def read(cls):
        raise NotImplementedError


class Environment(BaseLoader):
    """ Usage:
            Environment.read(prefix, source)

        Args:
            "prefix" will be added to all variables,
            for example: prefix_variable in uppercase

            "source" is a dictionary of names for finding variables,
            result will contain only variables that will be found.
    """

    @classmethod
    def read(cls, *args):
        result = {}
        for k, v in args[1].items():
            var_name = (args[0] + '_' + k).upper()
            value = environ.get(var_name, None)
            if value:
                result.update({k: value})
        return result


class File(BaseLoader):
    """ Usage:
            File.read(prefix, source, file_path)

        It works in the same way as the environment class,
        except for the additional argument containing
        path to the readable file.
    """

    drivers = (
        Json,
        Yaml
    )

    @classmethod
    def read(cls, *args):
        for driver in cls.drivers:
            try:
                result = {}
                read = driver.read(args[2])[args[0]]
                for k, v in args[1].items():
                    value = read.get(k, None)
                    if value:
                        result.update({k: value})
                return result
            except Exception:
                continue
        return {}
