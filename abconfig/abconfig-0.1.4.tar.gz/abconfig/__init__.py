__version__ = '0.1.4'

from abc import ABC
from copy import deepcopy
from os import environ, getcwd

from .loaders import File, Environment


class ABConfig(ABC):
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
        return self._data[item]

    def __getattr__(self, attr):
        return getattr(self._data, attr)

    def __init__(self):
        self._data = self.make(*self._attrs)

    def make(self, *args):
        result = {}
        for name in args:
            defaults = getattr(self, name)
            result_for_name = deepcopy(defaults)
            for loader in self.loaders:
                if (loader.isdisabled(self.disabled_loaders) is True and
                        loader.isenabled(self.enabled_loaders) is False):
                    continue
                result_for_name.update(loader.read(name, defaults, self.filepath))
            result.update({name: result_for_name})
        return result

    def get(self, item=None):
        if not item:
            return self._data
        elif item not in self._data:
            raise KeyError(f'Variable "{item}" was not exist in "{self}" config')
        return self._data[item]

    @property
    def _attrs(self):
        result = []
        excluded_attrs = (
            'enabled_loaders',
            'disabled_loaders',
            'filepath',
        )
        for attr in type(self).__dict__.keys():
            if (attr[:2] != '__' and attr[:1] != '_' and
                    attr not in excluded_attrs):
                result.append(str(attr))
        return result
