import logging
import shutil
from typing import List
from enum import Enum, auto
from dataclasses import dataclass

from pydotfiles.common import OS, PackageManager
from pydotfiles.utils import run_command, run_command_with_communication


logger = logging.getLogger(__name__)


class LanguagePluginManager(Enum):
    """
    Represents a language plugin manager
    like pyenv-virtualenv
    """
    PYENV_VIRTUALENV = auto()

    @staticmethod
    def from_string(label):
        if label is None:
            raise KeyError("Enum: No language manager passed in")

        return LanguagePluginManager[label.upper().replace("-", "_")]


@dataclass
class VirtualEnvironment:
    version: str
    name: str


class LanguageEnvironmentPluginManager:

    def __init__(self, language_plugin_manager: LanguagePluginManager, virtual_environments: List[VirtualEnvironment]):
        self.language_plugin_manager = language_plugin_manager
        self.virtual_environments = virtual_environments

    @property
    def is_installed(self):
        if self.language_plugin_manager == LanguagePluginManager.PYENV_VIRTUALENV:
            current_installed_brew_packages = run_command("brew list")
            return "pyenv-virtualenv" in current_installed_brew_packages
        else:
            raise NotImplementedError(f"Language Environment Plugin Manager: Sorry, the requested language plugin manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new) [env_plugin_manager={self.language_plugin_manager}]")

    def install(self):
        if self.is_installed:
            logger.info(f"Language Environment Plugin Manager: Already installed language environment plugin manager [env_plugin_manager={self.language_plugin_manager}]")
            return

        host_system = OS.get_host_system()
        package_manager = OS.get_package_manager(host_system)

        if package_manager == PackageManager.BREW:
            install_language_environment_plugin_manager_via_homebrew(self.language_plugin_manager)
        else:
            raise NotImplementedError(f"Language Environment Plugin Manager: Sorry, the requested package manager is not currently supported [package_manager={package_manager}]")

    def install_virtual_environments(self):
        for virtual_environment in self.virtual_environments:
            if self.language_plugin_manager == LanguagePluginManager.PYENV_VIRTUALENV:
                install_virtual_environment_version_with_pyenv(virtual_environment)
            else:
                raise NotImplementedError(f"Language Environment Plugin Manager: Sorry, the requested language plugin manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new) [env_plugin_manager={self.language_plugin_manager}]")

    def uninstall(self):
        if not self.is_installed:
            logger.info(f"Language Environment Plugin Manager: Already uninstalled language environment plugin manager [env_plugin_manager={self.language_plugin_manager}]")
            return

        host_system = OS.get_host_system()
        package_manager = OS.get_package_manager(host_system)

        if package_manager == PackageManager.BREW:
            uninstall_language_environment_plugin_manager_via_homebrew(self.language_plugin_manager)
        else:
            raise NotImplementedError(f"Language Environment Plugin Manager: Sorry, the requested package manager is not currently supported [package_manager={package_manager}]")

    def uninstall_virtual_environments(self):
        for virtual_environment in self.virtual_environments:
            if self.language_plugin_manager == LanguagePluginManager.PYENV_VIRTUALENV:
                uninstall_virtual_environment_version_with_pyenv(virtual_environment)
            else:
                raise NotImplementedError(f"Language Environment Plugin Manager: Sorry, the requested language plugin manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new) [env_plugin_manager={self.language_plugin_manager}]")


"""
Homebrew functions
"""


def install_language_environment_plugin_manager_via_homebrew(language_plugin_manager):
    logger.info(f"Language Environment Plugin Manager: Installing environment manager [env_plugin_manager={language_plugin_manager}]")

    if language_plugin_manager == LanguagePluginManager.PYENV_VIRTUALENV:
        command = "brew install pyenv-virtualenv"
        run_command(command)
    else:
        raise NotImplementedError(f"Language Environment Plugin Manager: Sorry, the requested language manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new) [env_plugin_manager={language_plugin_manager}]")

    logger.info(f"Language Environment Plugin Manager: Successfully installed environment manager [env_plugin_manager={language_plugin_manager}]")


def uninstall_language_environment_plugin_manager_via_homebrew(language_plugin_manager):
    logger.info(f"Language Environment Plugin Manager: Uninstalling environment manager [env_plugin_manager={language_plugin_manager}]")

    if language_plugin_manager == LanguagePluginManager.PYENV_VIRTUALENV:
        command = "brew uninstall pyenv-virtualenv"
        run_command(command)
    else:
        raise NotImplementedError(f"Language Environment Plugin Manager: Sorry, the requested language manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new) [env_plugin_manager={language_plugin_manager}]")

    logger.info(f"Language Environment Plugin Manager: Successfully uninstalled environment manager [env_plugin_manager={language_plugin_manager}]")


"""
Pyenv functions
"""


def install_virtual_environment_version_with_pyenv(virtual_environment: VirtualEnvironment):
    logger.info(f"Language Environment Plugin Manager: Installing virtual environment [name={virtual_environment.name}, version={virtual_environment.version}]")

    # Makes sure that the virtual env hasn't been created yet
    check_command = "pyenv versions"
    check_response = run_command(check_command)

    if virtual_environment.name in check_response:
        logger.info(f"Language Environment Plugin Manager: Already installed the virtual environment [name={virtual_environment.name}, version={virtual_environment.version}]")
        return

    command = f"pyenv virtualenv {virtual_environment.version} {virtual_environment.name}"
    run_command(command)

    logger.info(f"Language Environment Plugin Manager: Successfully installed virtual environment [name={virtual_environment.name}, version={virtual_environment.version}]")


def uninstall_virtual_environment_version_with_pyenv(virtual_environment: VirtualEnvironment):
    logger.info(f"Language Environment Plugin Manager: Uninstalling virtual environment [name={virtual_environment.name}, version={virtual_environment.version}]")

    # Makes sure that the virtual env hasn't been created yet
    check_command = "pyenv versions"
    check_response = run_command(check_command)

    if virtual_environment.name not in check_response:
        logger.info(f"Language Environment Plugin Manager: Already uninstalled the virtual environment [name={virtual_environment.name}, version={virtual_environment.version}]")
        return

    command = f"pyenv uninstall {virtual_environment.name}"
    run_command_with_communication(command, "y\n")

    logger.info(f"Language Environment Plugin Manager: Successfully uninstalled virtual environment [name={virtual_environment.name}, version={virtual_environment.version}]")
