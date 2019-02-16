__version__ = '0.2.3'

from copy import deepcopy
from os import environ, getcwd

from .loaders import File, Environment


class ABConfig:
    loaders = (
        File,
        Environment
    )

    enabled_loaders = ()
    disabled_loaders = ()

    filepath = environ.get('CONFIG_PATH', getcwd() + '/config')

    def __str__(self):
        return type(self).__name__

    def __getitem__(self, item: str):
        return self.get(item)

    def __getattr__(self, attr):
        return getattr(self._data, attr)

    def __init__(self, prefix=None, **kwargs):
        if type(self).__name__ == 'ABConfig':
            raise NotImplementedError
        self._prefix = prefix
        self._data = self.make(**self._attrs(**kwargs))

    def make(self, **kwargs):
        result = {}
        for name, defaults in kwargs.items():
            result_for_name = deepcopy(defaults)
            for loader in self.loaders:
                if (loader.isdisabled(self.disabled_loaders) is True and
                        loader.isenabled(self.enabled_loaders) is False):
                    continue

                if (isinstance(result_for_name, int) or
                        isinstance(result_for_name, str) or
                        isinstance(result_for_name, bool) or
                        isinstance(result_for_name, list) or
                        isinstance(result_for_name, tuple)):

                    read = loader.read(self._prefix, (name,), self.filepath)
                    if read:
                        result_for_name = read[name]
                        continue

                if isinstance(result_for_name, dict):
                    read = loader.read(name, defaults.keys(), self.filepath)
                    result_for_name.update(read)

            result.update({name: result_for_name})
        return result

    def get(self, item=None):
        if not item:
            return self._data
        elif item not in self._data:
            for key, values in self._data.items():
                if isinstance(values, dict) and item in values.keys():
                    return values[item]
            raise KeyError(f'Variable "{item}" was not exist in "{self}" config')
        return self._data[item]

    def _attrs(self, **kwargs):
        result = {}
        excluded_attrs = (
            'enabled_loaders',
            'disabled_loaders',
            'filepath',
        )
        for attr in type(self).__dict__.keys():
            if (attr[:2] != '__' and attr[:1] != '_' and
                    attr not in excluded_attrs):
                result.update({str(attr): getattr(self, attr)})

        if kwargs:
            result.update(kwargs)
        return result
