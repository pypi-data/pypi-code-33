import logging
import shutil
from typing import Optional, List
from enum import Enum, auto

from .plugins import LanguagePluginManager, LanguageEnvironmentPluginManager, VirtualEnvironment
from pydotfiles.common import OS, PackageManager
from pydotfiles.utils import run_command, run_command_with_communication


logger = logging.getLogger(__name__)


class LanguageManager(Enum):
    """
    Represents a language manager like
    pyenv, rbenv, goenv, jenv, etc.
    """
    PYENV = auto()
    RBENV = auto()
    GOENV = auto()
    JENV = auto()

    @staticmethod
    def from_string(label):
        if label is None:
            raise KeyError("Enum: No language manager passed in")

        return LanguageManager[label.upper()]


class LanguageEnvironmentManager:

    def __init__(self, language_manager: LanguageManager, sudo_password="", language_plugin_managers: Optional[List[LanguageEnvironmentPluginManager]] = None):

        if language_plugin_managers is None:
            language_plugin_managers = []

        self.language_manager = language_manager
        self.sudo_password = sudo_password
        self.language_plugin_managers = language_plugin_managers

    @property
    def is_installed(self):
        if self.language_manager == LanguageManager.PYENV:
            return shutil.which("pyenv") is not None
        elif self.language_manager == LanguageManager.JENV:
            return shutil.which("jenv") is not None
        else:
            raise NotImplementedError("Language Environment Manager: Sorry, the requested language manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new)")

    def install(self):
        if self.is_installed:
            logger.info(f"Language Environment Manager: Already installed language environment manager [env_manager={self.language_manager}]")
            return

        install_language_environment_manager(self.language_manager)

    def install_plugins(self):
        for language_plugin in self.language_plugin_managers:
            language_plugin.install()
            language_plugin.install_virtual_environments()

    def install_language_version(self, version):
        install_language(self.language_manager, version, self.sudo_password)

    def uninstall(self):
        if not self.is_installed:
            logger.info(f"Language Environment Manager: Already uninstalled language environment manager [env_manager={self.language_manager}]")
            return

        uninstall_language_environment_manager(self.language_manager)

    def uninstall_plugins(self):
        for language_plugin in self.language_plugin_managers:
            language_plugin.uninstall_virtual_environments()
            language_plugin.uninstall()

    def uninstall_language_version(self, version):
        uninstall_language(self.language_manager, version, self.sudo_password)


class DevelopmentEnvironment:
    """
    Class representing a dev environment, such as
    python, ruby, or java
    """

    def __init__(self, language: str, versions: List[str], language_environment_manager: LanguageEnvironmentManager):
        self.language = language
        self.versions = versions
        self.language_environment_manager = language_environment_manager

    def install(self):
        logger.info(f"Development Environment: Installing [lang={self.language}, versions={self.versions}, env_manager={self.language_environment_manager}")
        self.language_environment_manager.install()

        # Installs the base version
        for version in self.versions:
            self.language_environment_manager.install_language_version(version)

        # Installs any plugins
        self.language_environment_manager.install_plugins()

        logger.info(f"Development Environment: Successfully installed [lang={self.language}, versions={self.versions}, env_manager={self.language_environment_manager}")

    def uninstall(self):
        logger.info(f"Development Environment: Uninstalling [lang={self.language}, versions={self.versions}, env_manager={self.language_environment_manager}")

        # Uninstalls any plugins
        self.language_environment_manager.uninstall_plugins()

        # Uninstalls the base version
        for version in self.versions:
            self.language_environment_manager.uninstall_language_version(version)

        self.language_environment_manager.uninstall()
        logger.info(f"Development Environment: Successfully uninstalled [lang={self.language}, versions={self.versions}, env_manager={self.language_environment_manager}")


"""
Switching-layer functions
"""


def install_language_environment_manager(env_manager):
    host_system = OS.get_host_system()
    package_manager = OS.get_package_manager(host_system)

    if package_manager == PackageManager.BREW:
        install_language_environment_manager_via_homebrew(env_manager)
    else:
        raise NotImplementedError(f"Language Environment Manager: Sorry, the requested package manager is not currently supported [package_manager={package_manager}]")


def install_language(env_manager, language_version, sudo_password=""):
    if env_manager == LanguageManager.PYENV:
        check_command = f"pyenv versions"
        check_response = run_command(check_command)

        if language_version in check_response:
            logger.info(f"Language Environment Manager: Already installed language version [language=python, version={language_version}]")
            return

        logger.info(f"Language Environment Manager: Installing language version (this might take a bit, ~2 min) [language=python, version={language_version}]")

        command = f"pyenv install {language_version}"
        run_command(command)

        logger.info(f"Language Environment Manager: Successfully installed language version [language=python, version={language_version}]")
    elif env_manager == LanguageManager.JENV:
        host_system = OS.get_host_system()
        package_manager = OS.get_package_manager(host_system)

        if package_manager == PackageManager.BREW:
            install_java_version_via_homebrew(language_version, sudo_password)
        else:
            raise NotImplementedError(f"Language Environment Manager: Sorry, the requested package manager is not currently supported [package_manager={package_manager}]")
    else:
        raise NotImplementedError("Language Environment Manager: Sorry, the requested language manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new)")


def uninstall_language_environment_manager(env_manager):
    host_system = OS.get_host_system()
    package_manager = OS.get_package_manager(host_system)

    if package_manager == PackageManager.BREW:
        uninstall_language_environment_manager_via_homebrew(env_manager)
    else:
        raise NotImplementedError(f"Language Environment Manager: Sorry, the requested package manager is not currently supported [package_manager={package_manager}]")


def uninstall_language(env_manager, language_version, sudo_password=""):
    if env_manager == LanguageManager.PYENV:
        check_command = f"pyenv versions"
        check_response = run_command(check_command)

        if language_version not in check_response:
            logger.info(f"Language Environment Manager: Already uninstalled language version [language=python, version={language_version}]")
            return

        logger.info(f"Language Environment Manager: Uninstalling language version [language=python, version={language_version}]")

        command = f"pyenv uninstall {language_version}"
        run_command_with_communication(command, "y\n")  # The 'y\n' is to confirm that we want to uninstall the given python version

        logger.info(f"Language Environment Manager: Successfully uninstalled language version [language=python, version={language_version}]")
    elif env_manager == LanguageManager.JENV:
        host_system = OS.get_host_system()
        package_manager = OS.get_package_manager(host_system)

        if package_manager == PackageManager.BREW:
            uninstall_java_version_via_homebrew(language_version, sudo_password)
        else:
            raise NotImplementedError(f"Language Environment Manager: Sorry, the requested package manager is not currently supported [package_manager={package_manager}]")
    else:
        raise NotImplementedError("Language Environment Manager: Sorry, the requested language manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new)")


"""
Homebrew functions
"""

LATEST_CURRENT_JAVA_VERSION_IN_HOMEBREW = "11"


def install_language_environment_manager_via_homebrew(env_manager):
    logger.info(f"Language Environment Manager: Installing environment manager [env_manager={env_manager}]")
    if env_manager == LanguageManager.PYENV:
        command = "brew install pyenv"
        run_command(command)
    elif env_manager == LanguageManager.JENV:
        command = "brew install jenv"
        run_command(command)
    else:
        raise NotImplementedError("Language Environment Manager: Sorry, the requested language manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new)")

    logger.info(f"Language Environment Manager: Successfully installed environment manager [env_manager={env_manager}]")


def uninstall_language_environment_manager_via_homebrew(env_manager):
    if env_manager == LanguageManager.PYENV:
        command = "brew uninstall pyenv"
        run_command(command)
    elif env_manager == LanguageManager.JENV:
        command = "brew uninstall jenv"
        run_command(command)
    else:
        raise NotImplementedError("Language Environment Manager: Sorry, the requested language manager is not currently supported (feel free to open an issue at https://github.com/JasonYao/pydotfiles/issues/new)")


def install_java_version_via_homebrew(language_version, sudo_password=""):
    # Checks to make sure that we haven't already installed this java version
    check_command = f"brew cask list"
    check_response = run_command(check_command)

    if (language_version == "latest" or language_version == LATEST_CURRENT_JAVA_VERSION_IN_HOMEBREW) and "java " in check_response:
        logger.info(f"Language Environment Manager: Already installed language version [language=java, version={language_version}]")
        return
    elif language_version == "8" and "java8" in check_response:
        logger.info(f"Language Environment Manager: Already installed language version [language=java, version={language_version}]")
        return

    # Actually installs java
    logger.info(f"Language Environment Manager: Installing language version (takes a bit, ~2 min) [language=java, version={language_version}]")

    if language_version != "8" and language_version != LATEST_CURRENT_JAVA_VERSION_IN_HOMEBREW and language_version != "latest":
        raise ValueError(f"Language Environment Manager: Due to a limitation in Homebrew, we are unable to install any Java versions besides Java 8 and the latest Java (currently version {LATEST_CURRENT_JAVA_VERSION_IN_HOMEBREW})")

    if language_version == LATEST_CURRENT_JAVA_VERSION_IN_HOMEBREW or language_version == "latest":
        command = f"brew cask install java"
        run_command_with_communication(command, sudo_password)
        return

    # Getting java 8 requires getting versioned casks (note that there isn't a java9, java10, or java11 versioned cask)
    command = f"brew tap homebrew/cask-versions"
    run_command(command)

    command = f"brew cask install java8"
    run_command_with_communication(command, sudo_password)

    logger.info(f"Language Environment Manager: Successfully installed language version [language=java, version={language_version}]")


def uninstall_java_version_via_homebrew(language_version, sudo_password=""):
    logger.info(f"Language Environment Manager: Uninstalling language version [language=java, version={language_version}]")

    if language_version != "8" and language_version != LATEST_CURRENT_JAVA_VERSION_IN_HOMEBREW and language_version != "latest":
        raise ValueError(f"Language Environment Manager: Due to a limitation in Homebrew, we are unable to uninstall any Java versions besides Java 8 and the latest Java (currently version {LATEST_CURRENT_JAVA_VERSION_IN_HOMEBREW})")

    if language_version == LATEST_CURRENT_JAVA_VERSION_IN_HOMEBREW or language_version == "latest":
        command = f"brew cask uninstall java"
        run_command_with_communication(command, sudo_password)
        return

    # Getting java 8 requires getting versioned casks (note that there isn't a java9, java10, or java11 versioned cask)
    command = f"brew tap homebrew/cask-versions"
    run_command(command)

    command = f"brew cask uninstall java8"
    run_command_with_communication(command, sudo_password)

    logger.info(f"Language Environment Manager: Successfully uninstalled language version [language=java, version={language_version}]")
