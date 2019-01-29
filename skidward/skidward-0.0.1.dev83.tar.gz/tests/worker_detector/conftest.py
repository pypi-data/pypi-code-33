from typing import Optional, Dict
import pkg_resources as pkg

import pytest

from worker_detector.namespace_module_manager import NamespaceModuleManager


@pytest.fixture
def real_namespace() -> str:
    return "skidward.real.name.space"


class MockEntryPoint(pkg.EntryPoint):
    def __init__(self, name, module_name):
        self.name = name
        self.module_name = module_name

    def load(self, *args, **kwargs) -> pkg.EntryPoint:
        return MockEntryPoint(self.name, self.module_name)


class MockNamespaceModuleManager(NamespaceModuleManager):
    def _get_module_entry_points_on_namespace(self) -> Dict[str, pkg.EntryPoint]:
        if self.namespace == "skidward.real.name.space":
            return {
                "real_name": MockEntryPoint("real-name", "real_name"),
                "other_name": MockEntryPoint("other-name", "other_name"),
            }

        return super()._get_module_entry_points_on_namespace()


@pytest.fixture
def mock_namespace_module_manager() -> MockNamespaceModuleManager:
    return MockNamespaceModuleManager("skidward.real.name.space")


def mock_create_namespace_module_manager(namespace: str) -> MockNamespaceModuleManager:
    return MockNamespaceModuleManager(namespace)
