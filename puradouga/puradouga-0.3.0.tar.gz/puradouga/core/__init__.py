import dis
import hashlib
import inspect
import itertools
import logging
import os
from copy import deepcopy
from io import StringIO
from dataclasses import dataclass, field
from types import ModuleType
from typing import ClassVar, List, Optional, Dict, Callable

from puradouga.core.helper import args_kwargs_decorator, order_by_list, filter_by_list
from . import loader


class PluginBase(object):

    logger = logging.getLogger(__name__)

    def __implementation_hash__(self):
        with StringIO() as out:
            dis.dis(self.__class__, file=out)
            return int(hashlib.md5(out.getvalue().encode("utf-8")).hexdigest(), 16)

    @classmethod
    def __base_plugins__(cls):
        for plugin_base in cls.__bases__:
            if not issubclass(plugin_base, PluginBase):
                continue

            yield plugin_base

    @classmethod
    def __implemented_methods__(cls):
        for plugin_base in cls.__base_plugins__():
            for attr in dir(plugin_base):
                if attr.startswith("_") or getattr(cls, attr) == getattr(plugin_base, attr):
                    continue

                yield attr


@dataclass
class PluginSource:
    logger = logging.getLogger(__name__)
    path: str
    modules: List[ModuleType] = field(default_factory=list)

    @classmethod
    def list_modules(cls, base: str) -> List[str]:
        result = []

        for element in os.listdir(base):
            path = os.path.join(base, element)
            if path.endswith(".py"):
                result.append(path)
            elif os.path.isdir(path) and "__init__.py" in os.listdir(path):
                result.append(path)

        cls.logger.debug(f"Found modules {result} within path {base}")
        return result

    def reload(self):
        self.modules = []
        path = os.path.abspath(self.path)

        elements = self.list_modules(path)
        self.modules = loader.load_plugin_modules(elements)
        self.logger.debug("System reloaded plugins")


class PluginSystem:

    logger = logging.getLogger(__name__)

    def __init__(self, auto_reload: bool = True, debug: bool = False):
        self._sources: List[PluginSource] = []
        self._bases: List[ClassVar[PluginBase]] = []
        self._auto_reload = auto_reload
        self._plugins: List[ClassVar[PluginBase]] = []
        self._debug: bool = debug
        self._filters: Dict[ClassVar[PluginBase], SystemFilter] = {}

    def register_source(self, path: str, auto_reload: Optional[bool] = None):
        self._sources.append(PluginSource(path))

        if (auto_reload is not None and auto_reload) or self._auto_reload:
            self.reload()

        return self

    def register_base_class(self, base: ClassVar[PluginBase], auto_reload: Optional[bool] = None):
        self._bases.append(base)

        if (auto_reload is not None and auto_reload) or self._auto_reload:
            self.reload(include_modules=False)

        return self

    def _reload_plugins(self):
        plugins = []
        for source in self._sources:
            for module in source.modules:
                for plugin_key in filter(lambda k: not k.startswith("_"), dir(module)):
                    plugin = getattr(module, plugin_key)
                    try:
                        if inspect.isclass(plugin) \
                                and any([issubclass(plugin, base) and plugin != base for base in self._bases]):
                            plugins.append(plugin())
                    except Exception as e:
                        if self._debug:
                            raise e

        self._plugins = plugins

    def get_filter(self, base_class: ClassVar[PluginBase]):
        return self._filters.setdefault(base_class, SystemFilter(self, base_class))

    def reload(self, include_modules: bool = True):
        if include_modules:
            for system in self._sources:
                system.reload()

        self._reload_plugins()

    @property
    def plugins(self):
        return self._plugins

    @property
    def debug(self):
        return self._debug


class SystemFilter:

    logger = logging.getLogger(__name__)

    def __init__(self, plugin_system: PluginSystem, base_class: ClassVar[PluginBase]):
        self._plugin_system = plugin_system
        self._base_class = base_class

    def list(self):
        return filter(lambda p: isinstance(p, self._base_class), self._plugin_system.plugins)

    def names(self):
        for p in self.list():
            yield p.__class__.__name__

    def data(self):
        for p in self.list():
            yield (p.__implementation_hash__(), p.__class__.__name__,)

    @args_kwargs_decorator({"args": [], "kwargs": {}})
    def eval_score(self, method: Callable, eval_function: Callable, max_results: int = 1, copy: bool = True,
                   args: Optional[list] = None, kwargs: Optional[dict] = None):
        results = self._call_plugins(method, eval_function, args, kwargs, copy)
        results = sorted(results, key=lambda r: r[0], reverse=True)
        results = itertools.islice(results, 0, max_results)
        for result in results:
            yield result

    @args_kwargs_decorator({"args": [], "kwargs": {}})
    def eval_simple(self, method: Callable, eval_function: Callable = lambda a: 1, max_results: Optional[int] = None,
                    copy: bool = True, args: Optional[list] = None, kwargs: Optional[dict] = None):
        results = self._call_plugins(method, eval_function, args, kwargs, copy)
        results = filter(lambda a: a[0], results)
        results = itertools.islice(results, 0, max_results)
        for result in results:
            yield result

    @args_kwargs_decorator({"args": [], "kwargs": {}})
    def eval_ordered(self, method: Callable, eval_function: Callable, max_results: int = 1, copy: bool = True,
                     plugin_name_order: List[str] = None, args: Optional[list] = None, kwargs: Optional[dict] = None):
        results = self._call_plugins(method, eval_function, args, kwargs, copy,
                                     order_method=order_by_list(plugin_name_order),
                                     filter_method=filter_by_list(plugin_name_order))

        results = filter(lambda a: a[0], results)
        results = itertools.islice(results, 0, max_results)
        for result in results:
            yield result

    def _call_plugins(self, method: Callable, eval_function: Callable, args: list, kwargs: dict,
                      copy: bool = True, order_method: Optional[Callable] = None,
                      filter_method: Optional[Callable] = None):

        plugins = self.list()

        if filter_method:
            self.logger.debug("Applying filter to plugin list")
            plugins = filter(filter_method, plugins)

        if order_method:
            self.logger.debug("Applying sorted to plugin list")
            plugins = sorted(plugins, key=order_method)

        plugins = list(plugins)
        self.logger.debug(f"Processing {len(plugins)}")

        for plugin in plugins:
            result = self._call_plugin(method, eval_function, plugin, args, kwargs, copy)
            if result:
                yield result

    def _call_plugin(self, method: Callable, eval_function: Callable, plugin: PluginBase,
                     args: list, kwargs: dict, copy: bool = True):
        try:
            if copy:
                args = deepcopy(args)
                kwargs = deepcopy(kwargs)

            plugin_method = getattr(plugin, method.__name__)
            plugin_name = plugin.__class__.__name__
            plugin_result = plugin_method(*args, **kwargs)
            plugin_score = eval_function(plugin_result)
            return plugin_score, plugin_result, plugin_name

        except Exception as e:
            if self._plugin_system.debug:
                raise e
            return None
