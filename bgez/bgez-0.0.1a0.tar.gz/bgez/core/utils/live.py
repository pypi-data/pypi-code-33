import types

from . import symbol
from . import loader
from . import proxy
from . import state

from . import Singleton

__all__ = [
    'LiveCoding', 'livecoding',
    'reload',
]

def reload(thing: object) -> bool:
    try:
        loader.reload(thing.__module__)
        return True
    except AttributeError:
        return False

class LiveCoding(Singleton):
    __slots__ = ['name', 'state', 'proxies']

    REGISTRY = {}

    reload = staticmethod(reload)

    @classmethod
    def __instance__(cls, name: str = __name__, *args, **kargs):
        return cls.REGISTRY.get(name, None)

    def __init__(self, name: str = __name__, enabled: bool = True):
        self.__class__.REGISTRY[name] = self
        self.state = state.State(enabled)
        self.proxies = {}
        self.name = name

    def register(self, enabled: bool = True, module: str = None) -> callable:
        '''Decorator to register the function or class'''
        def decorator(thing: object) -> object:
            nonlocal enabled, module
            id = symbol.getid(thing)

            if isinstance(module, types.ModuleType):
                module = module.__name__

            if module is None:
                try: module = thing.__module__
                except AttributeError:
                    raise ImportWarning(f'cannot find the module for {thing}')

            if module == '__main__':
                raise ImportWarning(f'cannot update {thing} from __main__')

            try:
                fake = self.proxies[id]
                if enabled and self.state:
                    fake._Proxy__set_target(thing)
            except LookupError:
                fake = self.proxies[id] = proxy.Proxy(thing)
            return fake
        return decorator

    def reload_all(self):
        modules = set()
        for value in self.proxies.values():
            try: modules.add(value.__module__)
            except AttributeError: pass
        loader.reload(*modules)

livecoding = LiveCoding()
