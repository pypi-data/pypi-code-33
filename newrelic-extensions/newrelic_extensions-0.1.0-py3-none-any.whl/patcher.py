import logging

from newrelic_extensions import hooks
from newrelic_extensions.hooks.base import BasePatch

from pike.discovery import py

log = logging.getLogger(__name__)


def can_import_required(patch):
    for module_name in patch.required_modules:
        try:
            py.get_module_by_name(module_name)
        except ModuleNotFoundError:
            return False

    return True


def patch_all(project_packages=None):
    all_patches = py.get_all_inherited_classes(hooks, BasePatch)

    for patch in all_patches:
        if can_import_required(patch):
            log.debug('Adding patch %s', patch.__name__)
            patch().instrument(project_packages)
