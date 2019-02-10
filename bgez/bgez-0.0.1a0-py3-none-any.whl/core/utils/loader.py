from typing import Any, Union, List, Iterable

from types import ModuleType

import importlib
import logging
import pkgutil
import sys
import os

__all__ = [
    'module', 'component', 'reload',
    'module_filter',
    'RELOAD_HOOK',
]

ModuleOrStr = Union[ModuleType, str]
RELOAD_HOOK = 'reload_hook'
MODULES = {}

def walk_namespaces(paths: List[str]) -> Iterable:
    '''\
    Walks namespaces even if they are not packages (simple directories)\n

    :param paths: list of paths to parcour\
    '''
    for path in paths:
        for file in os.listdir(path):
            filepath = os.path.join(path, file)
            name, ext = os.path.splitext(file)
            if os.path.isdir(filepath):
                is_pkg = os.path.exists(os.path.join(filepath, '__init__.py'))
                yield None, file, is_pkg
            elif ext in importlib.machinery.all_suffixes():
                yield None, name, False

def module_filter(name: str, paths: List[str]) -> bool:
    return not (name.startswith('.') or name.startswith('_'))
def module(
    package: ModuleType,
    recursion: int = 0,
    namespaces: bool = True,
    filter: Callable = module_filter,
    foreach: Callable = lambda x: x,
    reload: bool = False,
    logger: logging.Logger = None
    ) -> ModuleType:
    '''\
    Dynamic and recursive importation\n

    :param package: str or actual package to parse (`'a.b.c'` or `a.b.c`)\n
    :param recursion: int depth to parcour\n
    :param namespaces: bool allowing the parcour of namespaces as well\n
    :param filter: callable(name: str) -> bool should we dive into module ?\n
    :param foreach: callable(module) -> None callback to execute on each loaded module\n
    :param reload: bool reload the modules if already imported\n
    :param logger: logging.Logger for debug purposes\
    '''
    recursion = recursion and int(recursion)
    namespaces = bool(namespaces)
    reload = bool(reload)

    walk_packages = walk_namespaces if namespaces else pkgutil.walk_packages

    if reload:
        globals()['reload'](package)

    if isinstance(package, str):
        __import__(package) # initializing (hack)
        package = importlib.import_module(package)
    MODULES.setdefault(package.__name__, package)

    if logger:
        logger.warning('loaded %s', package)

    foreach(package) # callback on loaded module

    # recursively load submodules
    if (recursion is None or recursion > 0) \
    and hasattr(package, '__path__'):

        for _, name, is_pkg in walk_packages(package.__path__):
            subname = '{}.{}'.format(package.__name__, name)

            if not filter(name, package.__path__):
                continue

            module(subname,
                recursion=recursion and recursion-1,
                namespaces=namespaces,
                filter=filter,
                foreach=foreach,
                reload=reload,
                logger=logger,
            )

    return package

def reload(*modules: List[ModuleOrStr]) -> None:
    '''\
    Reloads modules, from str or module directly.\n

    :param modules: variable arguments of `str` or `modules` (`'a.b.c'` or `a.b.c`)\
    '''
    for module in modules:
        if module == '__main__':
            continue

        if isinstance(module, str):
            module = sys.modules.get(module, None)

        if isinstance(module, ModuleType):
            package = importlib.reload(module)
            hook = getattr(package, RELOAD_HOOK, None)

            if callable(hook):
                hook()

def component(package: ModuleOrStr, component: str, *args, **kargs) -> Any:
    '''\
    Fetch a nested member inside package\n

    :param package: str or module (`'a.b.c'` or `a.b.c`)\n
    :param component: str ('d.e')\
    '''
    package = module(package, *args, **kargs)
    object = package
    for member in component.split('.'):
        object = getattr(object, member)
    return object
