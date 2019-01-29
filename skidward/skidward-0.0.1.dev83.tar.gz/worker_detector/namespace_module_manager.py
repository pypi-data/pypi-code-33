"""Provides an API for module detection on the provided namespace"""
from typing import Dict, Optional, List

import pkg_resources as pkg


class NamespaceModuleManager(object):
    def __init__(self, namespace: str):
        self.namespace = namespace
        self._available_modules = self._get_module_entry_points_on_namespace()

    def _get_module_entry_points_on_namespace(self) -> Dict[str, pkg.EntryPoint]:
        modules: Dict[str, pkg.EntryPoint] = {}

        for ep in pkg.iter_entry_points(self.namespace):
            modules[ep.module_name] = ep

        return modules

    def _load_module_entry_point(self, name: str) -> Optional[pkg.EntryPoint]:
        ep = self._available_modules.get(name)
        if ep:
            return ep.load()

        raise ValueError("Module with name '{}' was not found.".format(name))

    def get_all_available_module_names(self) -> List[str]:
        if not self._available_modules:
            self._available_modules = self._get_module_entry_points_on_namespace()

        return list(self._available_modules.keys())

    def load_module(self, name: str) -> pkg.EntryPoint:
        return self._load_module_entry_point(name)
