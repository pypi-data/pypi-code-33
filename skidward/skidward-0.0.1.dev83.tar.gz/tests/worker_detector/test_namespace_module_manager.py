import pytest
from pkg_resources import EntryPoint

from .conftest import MockNamespaceModuleManager
from worker_detector.namespace_module_manager import NamespaceModuleManager


def test_create_a_new_namespace_module_manager(mock_namespace_module_manager):
    assert mock_namespace_module_manager is not None
    assert isinstance(mock_namespace_module_manager, NamespaceModuleManager)


def test_unique_namespace_per_module_manager():
    nmm_one = NamespaceModuleManager("skidward.tests.one")
    nmm_two = NamespaceModuleManager("skidward.tests.two")

    assert nmm_one.namespace != nmm_two.namespace


def test_empty_list_of_modules_for_fake_namespace():
    fake_nmm = NamespaceModuleManager("skidward.fake.name.space")
    assert fake_nmm.get_all_available_module_names() == []


def test_modules_found_for_mocked_real_namespace(mock_namespace_module_manager):
    modules = mock_namespace_module_manager.get_all_available_module_names()
    assert isinstance(modules, list)
    assert len(modules) > 0


def test_raise_error_when_loading_non_existing_module(mock_namespace_module_manager):
    with pytest.raises(ValueError):
        mock_namespace_module_manager.load_module("fake-name")


def test_load_existing_module(mock_namespace_module_manager):
    result = mock_namespace_module_manager.load_module("real_name")
    assert result is not None
    assert isinstance(result, EntryPoint)
    assert result.module_name == "real_name"


def test_unique_list_of_modules_per_module_manager_namespace():
    nmm_first = MockNamespaceModuleManager("skidward.real.name.space")
    nmm_second = MockNamespaceModuleManager("skidward.fake.name.space")

    available_modules_first = nmm_first.get_all_available_module_names()
    available_modules_second = nmm_second.get_all_available_module_names()

    assert isinstance(available_modules_first, list)
    assert available_modules_first != available_modules_second
    assert len(available_modules_first) > len(available_modules_second)
