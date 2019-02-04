
# encoding: utf-8

# =========================================
#       IMPORTS
# --------------------------------------

from __future__ import print_function # Python 2

import rootpath

rootpath.append()

import re
import mybad
import inspecta
import json

from os import environ
from collections import Iterator
from six import PY2, PY3, string_types

try:
    import __builtin__ # Python 2
except ImportError:
    import builtins as __builtin__ # Python 3


# =========================================
#       CONSTANTS
# --------------------------------------

DEFAULT_ENV_VALUE_CAST = True
DEFAULT_ENV_KEY_PATTERN = None
DEFAULT_ENV_INSPECT_INDENT = 4
DEFAULT_ENV_INSPECT_COLORS = True

IS_INTEGER = re.compile('^[+-]?[0-9]+$')
IS_FLOAT = re.compile('^[+-]?[0-9]+\\.[0-9]+$')
IS_NUMBER = re.compile('^[+-]?[0-9]+(?:\\.[0-9]+)?$')


# =========================================
#       ERRORS
# --------------------------------------

class EnvjoyError(mybad.Error):
    pass


# =========================================
#       CLASSES
# --------------------------------------

class Envjoy(object):

    def get(self,
        key = None,
        cast_to = None,
        value = None,
        silent = True,
    ):
        self.__class__._validate_cast_type(cast_to)

        # NOTE: no handler for `bytes` type for now, not sure if needed

        try:
            if key is None and value is None:
                raise EnvjoyError('Expected either `key` or `value` to be present')

            if not key is None:
                value = environ.get(key, None)

            parsed_value = value

            try:
                parsed_value = json.loads(parsed_value)

            except:
                try:
                    parsed_value = eval(parsed_value, {
                        '__builtins__': {} # more secure variant
                    })

                except:
                    pass

            try:
                is_int = re.match(IS_INTEGER, parsed_value)

                if is_int:
                    parsed_value = int(parsed_value)

            except:
                is_int = False

            try:
                is_float = re.match(IS_FLOAT, parsed_value)

                if is_float:
                    parsed_value = float(parsed_value)

            except:
                is_float = False

            try:
                is_number = re.match(IS_NUMBER, parsed_value)

                if is_number:
                    parsed_value = float(parsed_value)

            except:
                is_number = False

            if cast_to == bool:
                if parsed_value is None:
                    return bool()

                try:
                    parsed_value = int(parsed_value)
                except:
                    pass

                try:
                    parsed_value = bool(parsed_value)
                except:
                    parsed_value = False

            elif cast_to == int:
                if parsed_value is None:
                    return int()

                if isinstance(parsed_value, (tuple, list, dict)):
                    parsed_value = str(parsed_value)

                if isinstance(parsed_value, str):
                    parsed_value = re.sub(r'[\n\t\s\,]', '', parsed_value)
                    parsed_value = re.sub(r'[^0-9]+', '', parsed_value)

                try:
                    parsed_value = int(parsed_value)
                except:
                    parsed_value = 0

            elif cast_to == float:
                if parsed_value is None:
                    return float()

                if isinstance(parsed_value, (tuple, list, dict)):
                    parsed_value = str(parsed_value)

                if isinstance(parsed_value, str):
                    parsed_value = re.sub(r'[\n\t\s\,]', '', parsed_value)
                    parsed_value = re.sub(r'[^0-9]+', '', parsed_value)

                try:
                    parsed_value = float(parsed_value)
                except:
                    parsed_value = 0.0

            elif cast_to == str:
                if parsed_value is None:
                    return str()

                if isinstance(value, str):
                    return value

                else:
                    try:
                        parsed_value = str(parsed_value)
                    except:
                        parsed_value = json.dumps(parsed_value)
                        parsed_value = parsed_value.strip('"')

            elif cast_to == tuple:
                if parsed_value is None:
                    return tuple()

                if isinstance(parsed_value, str):
                    parsed_value = parsed_value.replace('(', '[')
                    parsed_value = parsed_value.replace(')', ']')

                    try:
                        parsed_value = json.loads(parsed_value)
                    except:
                        try:
                            parsed_value = eval(parsed_value, {
                                '__builtins__': {} # more secure variant
                            })
                        except:
                            pass

                if isinstance(parsed_value, dict):
                    parsed_value = tuple([parsed_value])

                else:
                    if not isinstance(parsed_value, (tuple, list)):
                        parsed_value = [parsed_value]

                    parsed_value = tuple(parsed_value)

                    mapped_value = []

                    for value in parsed_value:
                        if isinstance(value, (tuple, list)):
                            value = self.get(value = value, cast_to = tuple)

                        mapped_value.append(value)

                    parsed_value = tuple(mapped_value)

            elif cast_to == list:
                if parsed_value is None:
                    return list()

                if isinstance(parsed_value, str):
                    parsed_value = parsed_value.replace('(', '[')
                    parsed_value = parsed_value.replace(')', ']')

                    try:
                        parsed_value = json.loads(parsed_value)
                    except:
                        try:
                            parsed_value = eval(parsed_value, {
                                '__builtins__': {} # more secure variant
                            })
                        except:
                            pass

                if isinstance(parsed_value, dict):
                    parsed_value = list([parsed_value])

                else:
                    if not isinstance(parsed_value, (tuple, list)):
                        parsed_value = [parsed_value]

                    parsed_value = list(parsed_value)

                    mapped_value = []

                    for value in parsed_value:
                        if isinstance(value, (tuple, list)):
                            value = self.get(value = value, cast_to = list)

                        mapped_value.append(value)

                    parsed_value = list(mapped_value)

            elif cast_to == dict:
                if parsed_value is None:
                    return dict()

                if isinstance(parsed_value, str):
                    parsed_value = parsed_value.replace('(', '[')
                    parsed_value = parsed_value.replace(')', ']')

                    try:
                        parsed_value = json.loads(parsed_value)
                    except:
                        try:
                            parsed_value = eval(parsed_value, {
                                '__builtins__': {} # more secure variant
                            })
                        except:
                            pass

                if isinstance(parsed_value, (tuple, list)):
                    try:
                        parsed_value = dict(parsed_value)
                    except:
                        pass

                if not isinstance(parsed_value, dict):
                    return dict()

                parsed_value = dict(parsed_value)

            else:
                try:
                    parsed_value = cast_to(parsed_value)
                except:
                    pass

            if PY2:
                if parsed_value == 'True':
                    parsed_value = True

                elif parsed_value == 'False':
                    parsed_value = False

            return parsed_value

        except Exception as error:
            if not silent:
                raise EnvjoyError(error)

            return None

    def set(self,
        key,
        value,
        cast_to = None,
        silent = True,
    ):
        self.__class__._validate_cast_type(cast_to)

        try:
            key = str(key)

            if value is None:
                value = ''

            if isinstance(value, Iterator):
                value = list(value)

            if isinstance(value, dict):
                value = dict(value) # e.g. `OrderedDict`, et. al.

            if isinstance(value, list):
                value = list(value)

            try:
                value = str(value)
            except:
                try:
                    value = str(json.loads(json.dumps(value)))
                except:
                    pass

            environ[key] = value

            return value

        except Exception as error:
            if not silent:
                raise EnvjoyError(error)

            return None

    def delete(self,
        key,
        silent = True,
    ):
        try:
            value = environ.get(key)

            del environ[key]

            return value

        except Exception as error:
            if not silent:
                raise EnvjoyError(error)

            return None

    def exists(self,
        key,
        silent = True,
    ):
        try:
            return (key in self.keys())

        except Exception as error:
            if not silent:
                raise EnvjoyError(error)

            return None

    def clear(self,
        silent = True,
    ):
        try:
            return environ.clear()

        except Exception as error:
            if not silent:
                raise EnvjoyError(error)

            return None

    def size(self):
        try:
            return len(list(self.items()))

        except:
            if not silent:
                raise EnvjoyError(error)

            return 0

    def inspect(self,
        colors = None,
        indent = None,
    ):
        if colors is None:
            colors = DEFAULT_ENV_INSPECT_COLORS

        if indent is None:
            indent = DEFAULT_ENV_INSPECT_INDENT

        # BUG/FIXME: `inspecta` ignores `colors` unless passed as ENV variable

        return inspecta.inspect(self.todict(),
            colors = colors,
            indent = indent,
        )

    def print(self):
        # print(self.inspect())
        return __builtin__.print(self.inspect())

    def keys(self,
        pattern = None,
    ):
        pattern = self.__class__._get_key_pattern(pattern)

        keys = environ.keys()

        # TODO: wildcard or regex filter: None

        return keys

    def values(self,
        pattern = None,
        cast = None,
    ):
        cast = self.__class__._get_value_cast(cast)

        values = environ.values()

        values = map(lambda value: (
            self.get(value = value)
        ), values)

        # TODO: return casted values for each key
        return values

    def items(self,
        pattern = None,
        cast = None,
    ):
        cast = self.__class__._get_value_cast(cast)

        # TODO: return casted values for each key
        return zip(
            self.keys(pattern = pattern),
            self.values(pattern = pattern),
        )

    def tolist(self):
        return list(self.items())

    def todict(self):
        _dict = {}

        for key, value in self.items():
            _dict[key] = value

        return _dict

    def __getitem__(self, key):
        key, cast_to = self.__class__._parse_accessor_arg(key)

        return self.get(key, cast_to = cast_to)

    def __getattr__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        key, cast_to = self.__class__._parse_accessor_arg(key)

        return self.set(key, value, cast_to)

    def __setattr__(self, key, value):
        return self.set(key, value)

    def __delitem__(self, key):
        return self.delete(key, key)

    def __delattr__(self, key):
        return self.delete(key, key)

    def __contains__(self, key):
        return self.exists(key)

    def __len__(self):
        return self.size()

    def __repr__(self):
        return repr(self.todict())

    def __str__(self):
        return str(self.todict())

    def __iter__(self):
        return iter(self.items())

    def __bool__(self):
        return True

    def __nonzero__(self):
        return self.__bool__()

    # private

    @classmethod
    def _get_key_pattern(klass, default = None):
        pattern = environ.get('ENV_KEY_PATTERN')
        pattern = default or DEFAULT_ENV_KEY_PATTERN

        return pattern

    @classmethod
    def _get_value_cast(klass, default = None):
        cast = environ.get('ENV_VALUE_CAST')
        cast = default or DEFAULT_ENV_VALUE_CAST

        return cast

    @classmethod
    def _validate_cast_type(klass, cast_to):
        if cast_to:
            if not isinstance(cast_to, type):
                raise EnvjoyError('Expected second optional argument `cast_to` to be of type `{0}`, but was `{1}`.'.format(str(type(type)), str(type(cast_to))))

    @classmethod
    def _parse_accessor_arg(klass, arg):
        cast_to = None

        if isinstance(arg, tuple):
            key = arg[0]

            if len(arg) > 1:
                cast_to = arg[1]

        else:
            key = arg

        return (key, cast_to)


# =========================================
#       EXPORTS
# --------------------------------------

env = Envjoy()
