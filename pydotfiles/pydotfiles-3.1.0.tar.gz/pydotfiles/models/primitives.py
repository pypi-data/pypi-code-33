# General imports
import logging
from pathlib import Path
import os
import json

# Project imports
from .enums import FileActionType
from .constants import PYDOTFILES_CACHE_DIRECTORY
from pydotfiles.utils import copy_file, symlink_file, rm_file, unsymlink_file, mv_file, run_file
from pydotfiles.utils import is_copied, is_linked


"""
Project-specific object primitives that
are used in higher-class business logic
"""

logger = logging.getLogger(__name__)


class FileAction:
    """
    Class representing an action on a file that we should
    have convenience methods for
    """

    def __init__(self, action, origin, destination, run_as_sudo, sudo_password=None):
        self.action = action
        self.origin = origin
        self.destination = destination
        self.run_as_sudo = run_as_sudo
        self.sudo_password = sudo_password

    def __str__(self):
        if self.action == FileActionType.SCRIPT or self.action == FileActionType.UNDO_SCRIPT:
            return f"{'SUDO ' if self.run_as_sudo else ''}{self.action.name} file={self.origin}, undo_file={self.destination}"
        return f"{'SUDO ' if self.run_as_sudo else ''}{self.action.name} {self.origin} -> {self.destination}"

    @property
    def is_completed(self):
        if self.action == FileActionType.COPY:
            return is_copied(self.origin, self.destination)
        elif self.action == FileActionType.SYMLINK:
            return is_linked(self.origin, self.destination)
        else:
            raise NotImplementedError(f"File Action: The action `{self.action}` is not supported yet (feel free to open a ticket on github!)")

    @property
    def reverse_action(self):
        return FileActionType.get_reverse(self.action)

    @property
    def destination_backup(self):
        return f"{self.destination}.backup"

    def do(self):
        logger.debug(f"File Action: Starting action [action={self.action}, origin={self.origin}, destination={self.destination}, use_sudo={self.run_as_sudo}]")
        if self.action == FileActionType.COPY:
            copy_file(self.origin, self.destination, self.run_as_sudo, self.sudo_password)
        elif self.action == FileActionType.SYMLINK:
            symlink_file(self.origin, self.destination, self.run_as_sudo, self.sudo_password)
        elif self.action == FileActionType.SCRIPT:
            run_file(self.origin, self.run_as_sudo, self.sudo_password)
        else:
            raise NotImplementedError(f"File Action: The action `{self.action}` is not supported yet (feel free to open a ticket on github!)")

        logger.debug(f"File Action: Successful action [action={self.action}, origin={self.origin}, destination={self.destination}, use_sudo={self.run_as_sudo}]")

    def undo(self):
        logger.debug(f"File Action: Starting undo action [action={self.reverse_action}, file={self.destination}, use_sudo={self.run_as_sudo}]")

        if self.destination is None:
            logger.info(f"File Action: No reverse action required [action={self.reverse_action}], file={self.destination}, use_sudo={self.run_as_sudo}")
            return

        if self.action == FileActionType.COPY:
            if not os.path.isfile(self.destination):
                logger.info(f"File Action: No reverse action required [action={self.reverse_action}], file={self.destination}, use_sudo={self.run_as_sudo}")
                return

            rm_file(self.destination, self.run_as_sudo, self.sudo_password)
        elif self.action == FileActionType.SYMLINK:
            if not os.path.islink(self.destination):
                logger.info(f"File Action: No reverse action required [action={self.reverse_action}], file={self.destination}, use_sudo={self.run_as_sudo}")
                return

            unsymlink_file(self.destination, self.run_as_sudo, self.sudo_password)
        elif self.action == FileActionType.SCRIPT:
            run_file(self.destination, self.run_as_sudo, self.sudo_password)
        else:
            raise NotImplementedError(f"File Action: The undo action `{self.action}` is not supported yet (feel free to open a ticket on github!)")

        logger.debug(f"File Action: Successful undo action [action={self.reverse_action}, file={self.destination}, use_sudo={self.run_as_sudo}]")

    def overwrite(self):
        # Just deletes the destination and then re-runs the operation
        logger.debug(f"File Action: Overwriting destination file [destination={self.destination}]")
        rm_file(self.destination, self.run_as_sudo, self.sudo_password)
        logger.debug(f"File Action: Successfully primed overwrite [destination={self.destination}]")

        self.do()

    def backup(self):
        logger.debug(f"File Action: Backing up file first [original={self.destination}, backup={self.destination_backup}]")
        mv_file(self.destination, self.destination_backup, self.run_as_sudo, self.sudo_password)
        logger.debug(f"File Action: Successfully backed up file first [original={self.destination}, backup={self.destination_backup}]")

        self.do()


class CacheDirectory:
    """
    Class representing the cache directory
    where we end up storing configurations
    related to the project
    """

    def __init__(self, package_manager=None, cache_directory=PYDOTFILES_CACHE_DIRECTORY):
        self.cache_directory = cache_directory
        self.package_manager = package_manager

        self.installed_packages = None
        self.installed_applications = None

        if package_manager is not None:
            self.reload_packages()
            self.reload_applications()

    @property
    def config_file(self):
        return f"{self.cache_directory}/config.json"

    @property
    def application_cache_file(self):
        return f"{self.cache_directory}/{self.package_manager.name.lower()}-application-cache"

    @property
    def package_cache_file(self):
        return f"{self.cache_directory}/{self.package_manager.name.lower()}-package-cache"

    @property
    def is_created(self):
        return os.path.isdir(self.cache_directory)

    """
    Config-file methods
    """

    def write_to_config(self, data):
        self.__idempotent_create__()

        with open(self.config_file, 'w') as config_file:
            config_file.write(json.dumps(data, sort_keys=True, indent=4))

    def read_from_config(self):
        if not os.path.isfile(self.config_file):
            return {}

        with open(self.config_file, 'r') as config_file:
            return json.load(config_file)

    """
    Public cache accessors
    """

    def is_package_installed(self, package):
        if self.installed_packages is None:
            return False

        return package in self.installed_packages

    def is_application_installed(self, application):
        if self.installed_applications is None:
            return False

        return application in self.installed_applications

    """
    Public cache updaters
    """

    def overwrite_packages(self, packages):
        self.__overwrite_cache_file__(self.package_cache_file, packages)

    def overwrite_applications(self, applications):
        self.__overwrite_cache_file__(self.application_cache_file, applications)

    def append_package(self, package):
        self.__append_to_cache_file__(self.package_cache_file, package)

    def append_application(self, application):
        self.__append_to_cache_file__(self.application_cache_file, application)

    def reload_packages(self):
        self.installed_packages = self.__read_from_cache_file__(self.package_cache_file)

    def reload_applications(self):
        self.installed_applications = self.__read_from_cache_file__(self.application_cache_file)

    """
    Internal helper methods
    """

    def __idempotent_create__(self):
        if self.is_created:
            logger.debug(f"Caching: Cache directory was already created [directory={self.cache_directory}]")
            return

        logger.debug(f"Caching: No cache directory was found, creating now [directory={self.cache_directory}]")
        Path(self.cache_directory).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Caching: Successfully created cache directory [directory={self.cache_directory}]")

    def __overwrite_cache_file__(self, cache_file, data):
        self.__idempotent_create__()
        with open(cache_file, "w") as cache_file:
            cache_file.write(f"{data}\n")

    @staticmethod
    def __append_to_cache_file__(cache_file, data):
        with open(cache_file, "a") as cache_file:
            cache_file.write(f"{data}\n")

    def __read_from_cache_file__(self, cache_file):
        if os.path.isdir(self.cache_directory):
            if os.path.isfile(cache_file):
                with open(cache_file) as cache_file_descriptor:
                    cached_data = {line.rstrip('\n') for line in cache_file_descriptor}
                    logger.debug(f"Caching: Loaded in cache data [file={cache_file}, data={cached_data}")
                    return cached_data
            else:
                logger.debug(f"Caching: No cache file found [file={cache_file}]")
        else:
            logger.debug(f"Caching: No cache directory found [directory={self.cache_directory}]")
        return None
