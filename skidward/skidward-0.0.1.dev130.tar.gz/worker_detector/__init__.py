from typing import List, Optional

from pkg_resources import EntryPoint

from worker_detector.namespace_module_manager import NamespaceModuleManager


__NAMESPACE = "skidward.workers"


def create_namespace_module_manager(namespace: str = None) -> NamespaceModuleManager:
    return NamespaceModuleManager(namespace or __NAMESPACE)


def get_all_workers_on_namespace(namespace: str = None) -> List[str]:
    nmm = create_namespace_module_manager(namespace)
    return nmm.get_all_available_module_names()


def load_worker_on_namespace(
    worker_name: str, namespace: str = None
) -> Optional[EntryPoint]:
    worker = None
    nmm = create_namespace_module_manager(namespace)

    try:
        worker = nmm.load_module(worker_name)
    except ValueError:
        print(f"No worker could be loaded by the name {worker_name}.")

    return worker
