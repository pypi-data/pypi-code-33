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
        for key in args[1]:
            var_name = args[0] + '_' + key if args[0] else key
            value = environ.get(var_name.upper(), None)
            if value:
                result.update({key: value})
        return result


class File(BaseLoader):
    """ Usage:
            File.read(prefix, source, filepath)

        It works in the same way as the environment class,
        except for the additional argument containing
        path to the readable file.
    """

    drivers = (
        Json,
        Yaml,
    )

    @staticmethod
    def read_file(filepath, drivers, section):
        for driver in drivers:
            try:
                read = driver.read(filepath)
                if not section in read:
                    for value in read.values():
                        if isinstance(value, dict) and section in value:
                            return value[section]

                return read[section]
            except Exception:
                continue
        return {}

    @classmethod
    def read(cls, *args):
        result = {}
        for key in args[1]:
            read = cls.read_file(args[2], cls.drivers, args[0])
            value = read.get(key, None)
            if value:
                result.update({key: value})
        return result
