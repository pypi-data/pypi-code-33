# General imports
import configparser
import shutil
import os
import subprocess
import sys
import re
from subprocess import Popen, PIPE, TimeoutExpired
from distutils.version import StrictVersion
import logging

# Vendor imports
from git import Repo
from git.remote import RemoteProgress
from progressbar import ProgressBar

# Project imports
from .enums import FileActionType, OverrideAction
from .constants import *
from .primitives import FileAction, CacheDirectory
from .exceptions import PydotfilesError, PydotfilesErrorReason, ValidationError
from .validator import Validator

from .utils import install_homebrew, uninstall_homebrew, load_data_from_file
from .utils import get_user_override, ask_sudo_password
from .dock import DockManager
from pydotfiles.utils import remove_prefix
from pydotfiles.defaults import get_current_mac_version
from .utils import set_logging
from pydotfiles.loading import get_os_default_settings
from pydotfiles.common import OS, PackageManager
from pydotfiles.loading import parse_developer_environments


logger = logging.getLogger(__name__)


class Dotfiles:
    """
    Class representing the dotfiles that
    we are reading in
    """

    def __init__(self, config_repo_local, config_repo_remote, is_quiet, is_verbose, active_modules=None):
        self.config_repo_local = config_repo_local
        self.host_os = OS.from_string(sys.platform)
        self.cache_directory = CacheDirectory(package_manager=OS.get_package_manager(self.host_os))

        set_logging(is_quiet, is_verbose)

        if config_repo_remote is None:
            self.config_repo_remote = load_config_repo_remote(config_repo_local) if self.is_cloned else None
        else:
            self.config_repo_remote = config_repo_remote

        module_information = load_active_modules(config_repo_local, active_modules, self.host_os, self.cache_directory) if self.is_cloned else None

        self.modules = None if module_information is None else module_information[0]
        self.is_sudo_used = None if module_information is None else module_information[1]
        self.sudo_password = None

    def __str__(self):
        return f"Dotfiles [Config Directory={self.config_repo_local}, Config Remote={self.config_repo_remote}, Modules={self.modules}]"

    @property
    def is_cloned(self):
        return os.path.isdir(f"{self.config_repo_local}/.git")

    def download(self):
        """
        Dotfile configs haven't been cloned yet, so cloning
        from remote to local
        """
        if self.config_repo_remote is None:
            raise PydotfilesError(PydotfilesErrorReason.NO_REMOTE_REPO, "Download: No dotfiles configuration git remote link passed in (try running `pydotfiles download -r <git remote link>`)")

        logger.info(f"Download: Cloning git repository [remote={self.config_repo_remote}, local={self.config_repo_local}]")
        try:
            Repo.clone_from(self.config_repo_remote, self.config_repo_local, progress=GitRemoteProgress())
            logger.info(f"Download: Successfully cloned git repository [remote={self.config_repo_remote}, local={self.config_repo_local}]")
        except Exception:
            logger.exception(f"Download: Failed to clone git repository [Remote={self.config_repo_remote}, Local={self.config_repo_local}]")
            raise PydotfilesError(PydotfilesErrorReason.REMOTE_REPO_CLONE_ISSUE)

    def clean(self, target):
        """
        Deletes the downloaded dotfile configs directory
        """
        if target == "cache":
            if os.path.isdir(PYDOTFILES_CACHE_DIRECTORY):
                logger.info(f"Clean: Deleting the pydotfiles cache [Cache={PYDOTFILES_CACHE_DIRECTORY}]")
                shutil.rmtree(PYDOTFILES_CACHE_DIRECTORY)
                logger.info(f"Clean: Successfully deleted the pydotfiles cache [Cache={PYDOTFILES_CACHE_DIRECTORY}]")
            else:
                logger.info(f"Clean: The pydotfiles cache does not exist [Cache={PYDOTFILES_CACHE_DIRECTORY}]")
        elif target == "repo":
            if os.path.isdir(self.config_repo_local):
                logger.info(f"Clean: Deleting the pydotfiles configuration local repo [Local={self.config_repo_local}]")
                shutil.rmtree(self.config_repo_local)
                logger.info(f"Clean: Successfully deleted the pydotfiles configuration local repo [Local={self.config_repo_local}]")
            else:
                logger.info(f"Clean: The pydotfiles configuration local repo does not exist [Local={self.config_repo_local}]")
        else:
            raise PydotfilesError(PydotfilesErrorReason.UNKNOWN_CLEANING_TARGET, f"Clean: Unknown cleaning target passed in [target={target}]")

    """
    Installation methods
    """

    def install_all(self):
        # Propagates the sudo password for the program
        self.sudo_password = ask_sudo_password() if self.is_sudo_used else None
        self.__propagate_sudo_password__()

        for module_name, module in self.modules.items():
            module.install()

    def install_multiple_modules(self, module_names):
        # Propagates the sudo password for the program
        self.sudo_password = ask_sudo_password() if self.is_sudo_used else None
        self.__propagate_sudo_password__()

        for module_name in module_names:
            self.install_single_module(module_name)

    def install_single_module(self, module_name):
        module = self.modules.get(module_name)

        if module is None:
            raise PydotfilesError(PydotfilesErrorReason.UNKNOWN_MODULE_NAME, f"Module Installation: Failed to find the module `{module_name}` when trying to install")

        module.install()

    """
    Uninstallation methods
    """

    def uninstall_all(self, uninstall_packages, uninstall_applications, uninstall_environments):
        # Propagates the sudo password for the program
        self.sudo_password = ask_sudo_password() if self.is_sudo_used else None
        self.__propagate_sudo_password__()

        for module_name, module in self.modules.items():
            module.uninstall(uninstall_packages, uninstall_applications, uninstall_environments)

    def uninstall_multiple_modules(self, module_names, uninstall_packages, uninstall_applications, uninstall_environments):
        # Propagates the sudo password for the program
        self.sudo_password = ask_sudo_password() if self.is_sudo_used else None
        self.__propagate_sudo_password__()

        for module_name in module_names:
            self.uninstall_single_module(module_name, uninstall_packages, uninstall_applications, uninstall_environments)

    def uninstall_single_module(self, module_name, uninstall_packages, uninstall_applications, uninstall_environments):
        module = self.modules.get(module_name)
        if module is None:
            raise PydotfilesError(PydotfilesErrorReason.UNKNOWN_MODULE_NAME, f"Module Installation: Failed to find the module `{module_name}` when trying to uninstall")
        module.uninstall(uninstall_packages, uninstall_applications, uninstall_environments)

    def update(self):
        if self.config_repo_remote is None:
            raise PydotfilesError(PydotfilesErrorReason.NO_REMOTE_REPO, f"Update: No dotfiles configuration git remote link passed in")

        logger.info(f"Update: Pulling git repository [Remote={self.config_repo_remote}, Local={self.config_repo_local}]")
        try:
            Repo(self.config_repo_local).remote('origin').pull(progress=GitRemoteProgress())
            logger.info(f"Update: Successfully updated dotfiles git repository [Remote={self.config_repo_remote}, Local={self.config_repo_local}, Remote=Origin]")
        except Exception:
            logger.exception(f"Update: Failed to update git repository [Remote={self.config_repo_remote}, Local={self.config_repo_local}]")
            raise PydotfilesError(PydotfilesErrorReason.REMOTE_REPO_CLONE_ISSUE)

    def __propagate_sudo_password__(self):
        for module in self.modules.values():
            module.sudo_password = self.sudo_password
            module.__propagate_sudo_password__()


class Module:
    """
    Class representing a single module's configuration
    values
    """

    def __init__(self, name, directory, settings_file, start_file, post_file, undo_start_file, undo_post_file, symlinks, other_files, host_os, cache_directory):
        self.name = name
        self.directory = directory
        self.symlinks = symlinks
        self.other_files = other_files
        self.host_os = host_os
        self.cache_directory = cache_directory

        self.start_action = None if start_file is None else FileAction(FileActionType.SCRIPT, start_file, undo_start_file, None, None)
        self.post_action = None if post_file is None else FileAction(FileActionType.SCRIPT, post_file, undo_post_file, None, None)

        # Loads in the settings file
        self.settings_file = settings_file
        settings_data = load_data_from_file(self.settings_file)
        self.operating_system = parse_operating_system_config(settings_data.get('os'), self.cache_directory, self.directory)
        self.environments = parse_developer_environments(settings_data.get('environments'))
        self.actions, self.is_sudo_used = parse_action_configs(settings_data.get('actions'), self.directory, self.symlinks, self.other_files)
        self.sudo_password = None

    def __str__(self):
        return f"Module [Name={self.name}, Start={self.start_action}, Settings={self.settings_file}, Post={self.post_action}]"

    def install(self):
        if self.operating_system is not None and self.operating_system.name != self.host_os:
            logger.info(f"Install: Skipping operating system installation due to OS mismatch [HostOS={self.host_os}, ModuleOS={self.operating_system.name}]")
            return

        logger.info(f"Install: Installing module [name={self.name}]")

        if self.start_action is not None:
            self.start_action.do()

        if self.operating_system is not None:
            self.operating_system.install_packages()
            self.operating_system.install_applications()
            self.operating_system.install_settings()
            self.operating_system.install_default_dock()

        for environment in self.environments:
            environment.install()

        self.do_actions()

        if self.post_action is not None:
            self.post_action.do()

        logger.info(f"Install: Successfully installed module [name={self.name}]")

    def uninstall(self, uninstall_packages, uninstall_applications, uninstall_environments):
        if self.operating_system is not None and self.operating_system.name != self.host_os:
            logger.info(f"Uninstall: Skipping operating system uninstallation due to OS mismatch [HostOS={self.host_os}, ModuleOS={self.operating_system.name}]")
            return

        logger.info(f"Uninstall: Uninstalling module [name={self.name}]")

        if self.start_action is not None:
            self.start_action.undo()

        self.undo_actions()

        if uninstall_environments:
            for environment in self.environments:
                environment.uninstall()

        if self.operating_system is not None:
            if uninstall_applications:
                self.operating_system.uninstall_applications()

            if uninstall_packages:
                self.operating_system.uninstall_packages()

        if self.post_action is not None:
            self.post_action.undo()

        logger.info(f"Uninstall: Successfully uninstalled module [name={self.name}]")

    def do_actions(self):
        override_action = None
        for action in self.actions:
            try:
                override_action = self.__do_action_with_override__(override_action, action)
            except FileExistsError:
                logger.debug(f"Action: Failed to complete action [Action={action}]")
                override_action = get_user_override(action)
                override_action = self.__do_action_with_override__(override_action, action)

    def undo_actions(self):
        for file_action in self.actions:
            try:
                logger.info(f"Action: Starting undo action [Action={file_action}]")
                file_action.undo()
                logger.info(f"Action: Successfully undid action [Action={file_action}]")
            except Exception:
                logger.exception(f"Action: Failed to undo action [Action={file_action}]")
                raise

    @staticmethod
    def __do_action_with_override__(override_action, action):
        # Normal procedure
        if override_action is None:
            logger.info(f"Action: Starting action [Action={action}]")
            action.do()
            logger.info(f"Action: Successfully completed action [Action={action}]")
            return None

        # Skips the actions
        if override_action == OverrideAction.SKIP_FILE:
            logger.info(f"Action: Skipping action [Action={action}]")
            return None

        if override_action == OverrideAction.SKIP_ALL_FILES:
            logger.info(f"Action: Skipping all actions [Action={action}]")
            return OverrideAction.SKIP_ALL_FILES

        # Overwrites the actions
        if override_action == OverrideAction.OVERWRITE_FILE:
            logger.info(f"Action: Overwriting action destination [Action={action}]")
            action.overwrite()
            return None

        if override_action == OverrideAction.OVERWRITE_ALL_FILES:
            logger.info(f"Action: Overwriting all action's destinations [Action={action}]")
            action.overwrite()
            return OverrideAction.OVERWRITE_ALL_FILES

        # Backs up first before performing the action
        if override_action == OverrideAction.BACKUP_FILE:
            logger.info(f"Action: Backing up first for action [Action={action}]")
            action.backup()
            return None

        if override_action == OverrideAction.BACKUP_ALL_FILES:
            logger.info(f"Action: Backing up first for all actions [Action={action}]")
            action.backup()
            return None

    def __propagate_sudo_password__(self):
        for action in self.actions:
            action.sudo_password = self.sudo_password

        if self.operating_system is not None:
            self.operating_system.sudo_password = self.sudo_password

        if self.start_action is not None:
            self.start_action.sudo_password = self.sudo_password

        if self.post_action is not None:
            self.post_action.sudo_password = self.sudo_password


class OperatingSystem:
    """
    Class representing configurations for a given
    operating system
    """

    def __init__(self, name, shell, packages, applications, cache_directory, default_dock, settings, dock_manager):
        self.name = OS.from_string(name)
        self.shell = shell
        self.package_manager = OS.get_package_manager(self.name)
        self.packages = packages
        self.applications = applications
        self.cache_directory = cache_directory
        self.default_dock = default_dock
        self.settings = settings
        self.dock_manager = dock_manager
        self.sudo_password = None

    def install_package_manager(self):
        if self.name == OS.MACOS:
            install_homebrew()
        else:
            logger.warning(f"Package Manager: Support for package manager is not implemented yet [action=install, package manager={self.package_manager}]")

    def install_packages(self):
        for package in self.packages:
            self.install_package(package)

    def install_applications(self):
        for application in self.applications:
            self.install_application(application)

    def install_default_dock(self):
        if self.name != OS.MACOS:
            logger.info("Default Dock: Setting the dock is currently only supported on macOS- feel free to leave a github issue at https://github.com/JasonYao/pydotfiles/issues/new to request this feature!")
            return

        if self.default_dock is None:
            logger.info("Default Dock: No default dock specified, skipping dock setting")
            return

        current_dock_applications = self.dock_manager.get_current_dock_applications()

        # Note: The ^ gives the disjunctive union (symmetric difference) of two sets
        symmetric_difference_in_dock_applications = self.default_dock ^ current_dock_applications

        if len(symmetric_difference_in_dock_applications) == 0:
            logger.info("Default Dock: All default dock applications already set")
            return

        logger.info(f"Default Dock: Found persistent apps on the dock that did not belong or missing default apps, resetting now [default_apps_difference={symmetric_difference_in_dock_applications}]")

        # In this scenario, we found persistent apps on the dock that
        # don't belong there, or missing default apps, so we'll delete
        # the existing dock config, add in our new one, and then restart
        # everything
        DockManager.delete_dock_plist_file()

        for default_dock_application in self.default_dock:
            DockManager.add_application_to_default_on_dock(default_dock_application)

        DockManager.restart_dock()
        logger.info(f"Default Dock: Successfully set the dock to have the default applications [default_applications={self.default_dock}]")

    def install_settings(self):
        current_mac_version = get_current_mac_version()
        for setting in self.settings:
            if setting.should_run(current_mac_version, self.sudo_password):
                logger.info(f"Setting: Default setting not set, setting now [default_setting={setting.name}, description={setting.description}]")
                setting.run(self.sudo_password)
            else:
                logger.info(f"Setting: Default setting already set [default_setting={setting.name}, description={setting.description}]")

    def uninstall_package_manager(self):
        if self.name == OS.MACOS:
            uninstall_homebrew()
        else:
            logger.warning(f"Package Manager: Support for package manager is not implemented yet [action=uninstall, package manager={self.package_manager}]")

    def uninstall_packages(self):
        for application in self.applications:
            self.uninstall_application(application)

    def uninstall_applications(self):
        for application in self.applications:
            self.uninstall_application(application)

    """
    Helper methods
    """

    def install_package(self, package_with_args):
        package = package_with_args.split()[0]

        if self.cache_directory.is_package_installed(package):
            logger.info(f"Package: Already installed [Package={package}]")
            return

        logger.info(f"Package: Starting installation [Package={package}]")

        if self.package_manager == PackageManager.BREW:
            command = f"brew install {package_with_args}"

            command_result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Version error-handling
            stderr = command_result.stderr.decode()
            if stderr == "":
                logger.info(f"Package: Successfully installed [Package={package}]")
            elif "is already installed and up-to-date" in stderr:
                logger.info(f"Package: Already installed and up to date [Package={package}]")
            elif "is already installed\n" in stderr:
                semver_extractor = re.compile("(\d+\.)(\d+\.?)(\d+\.?)?")
                all_semver = semver_extractor.findall(stderr)
                current_version = StrictVersion(''.join(all_semver[0]))
                latest_version = StrictVersion(''.join(all_semver[1]))
                logger.warning(f"Package: Installed but outdated [Package={package}, CurrentVersion={current_version}, LatestVersion={latest_version}, help=To update all your libraries, try running `pydotfiles update all` or `pydotfiles update {package}`]")
            else:
                raise NotImplementedError(f"Package: Failed to install package `{package}` [Stderr={stderr}]")

            # Dumps to the cache file after installation
            if os.path.isfile(self.cache_directory.package_cache_file):
                # Just appends the latest package to an existing cache
                self.cache_directory.append_package(package)
            else:
                logger.info(f"Caching: Dumping found packages into pydotfiles cache")
                # No cache was found, we do a full dump here at the start
                command = f"brew list"
                command_result = subprocess.run(command.split(), capture_output=True)
                package_dump = command_result.stdout.decode()
                self.cache_directory.overwrite_packages(package_dump)
                self.cache_directory.reload_packages()
        elif self.package_manager == PackageManager.APT or self.package_manager == PackageManager.YUM:
            # TODO P2: Clean up and fully flesh out support for *nix
            command = f"{self.package_manager} install -y {package}"

            process = Popen(['sudo', '-S'] + command.split(), stdin=PIPE, stderr=PIPE, universal_newlines=True)
            try:
                process.communicate(self.sudo_password + '\n')
            except TimeoutExpired:
                process.kill()
                logger.exception(f"Package: Installation failed [Package={package}]")
                raise

            logger.info(f"Package: Installation Successful [Package={package}]")

            # TODO P3: Put list of downloaded packages into cache
        else:
            raise NotImplementedError(f"Package: Install is currently not supported [PackageManager={self.package_manager}]")

    def install_application(self, application):
        if self.cache_directory.is_application_installed(application):
            logger.info(f"Application: Already installed [Application={application}]")
            return

        logger.info(f"Application: Starting installation [Application={application}]")

        if self.package_manager == PackageManager.BREW:
            command = f"brew cask install {application}"
            command_result = subprocess.run(command.split(), capture_output=True)

            stderr = command_result.stderr.decode()

            # Response code parsing
            if command_result.returncode == 0:
                logger.info(f"Application: Successfully installed [Application={application}]")
            elif "is already installed." in stderr:
                logger.info(f"Application: Already installed application [Application={application}]")
            else:
                logger.warning(f"Application: Failed to install [Application={application}, Stderr={stderr}]")

            # Dumps to the cache file after installation
            if os.path.isfile(self.cache_directory.application_cache_file):
                # Just appends the latest application to an existing cache
                self.cache_directory.append_application(application)
            else:
                logger.info(f"Caching: Dumping found applications into pydotfiles cache")
                # No cache was found, we do a full dump here at the start
                command = f"brew cask list"
                command_result = subprocess.run(command.split(), capture_output=True)
                applicatione_dump = command_result.stdout.decode()
                self.cache_directory.overwrite_applications(applicatione_dump)
                self.cache_directory.reload_applications()
        elif self.package_manager == PackageManager.APT or self.package_manager == PackageManager.YUM:
            # TODO P2: Clean up and fully flesh out support for *nix
            command = f"{self.package_manager} install -y {application}"

            process = Popen(['sudo', '-S'] + command.split(), stdin=PIPE, stderr=PIPE, universal_newlines=True)
            try:
                process.communicate(self.sudo_password + '\n')
            except TimeoutExpired:
                process.kill()
                logger.exception(f"Package: Installation failed [Application={application}]")
                raise

            logger.info(f"Application: Successfully installed [Application={application}]")
            # TODO P3: Put list of downloaded packages into cache
        else:
            raise NotImplementedError(f"Application: Install is currently not supported [Package Manager={self.package_manager}]")

    def uninstall_package(self, package):
        logger.info(f"Package: Starting uninstall [Package={package}]")

        if self.package_manager == PackageManager.BREW:
            command = f"brew uninstall {package}"
            command_result = subprocess.run(command.split())

            if command_result.returncode != 0:
                # TODO P3: replace with custom error
                logger.warning(f"Package: Failed to uninstall [Package={package}]")
                raise RuntimeError(f"Package: An issue occurred when trying to uninstall `{package}`")
        elif self.package_manager == PackageManager.APT or self.package_manager == PackageManager.YUM:
            command = f"{self.package_manager} uninstall -y {package}"

            process = Popen(['sudo', '-S'] + command.split(), stdin=PIPE, stderr=PIPE, universal_newlines=True)
            try:
                process.communicate(self.sudo_password + '\n')
            except TimeoutExpired:
                process.kill()
                logger.exception(f"Package: Failed to uninstall [Package={package}]")
                raise
        else:
            raise NotImplementedError(f"Package: Uninstall is currently not supported [Package Manager={self.package_manager}]")

        logger.info(f"Package: Successfully uninstalled [Package={package}]")

    def uninstall_application(self, application):
        logger.info(f"Application: Starting uninstall [Application={application}]")

        if self.package_manager == PackageManager.BREW:
            command = f"brew cask uninstall {application}"
            command_result = subprocess.run(command.split())

            if command_result.returncode != 0:
                logger.info(f"Application: Failed to uninstall [Application={application}]")
                raise RuntimeError(f"Application: An issue occurred when trying to uninstall `{application}`")

            logger.info(f"Application: Successfully uninstalled [Application={application}]")
        else:
            self.uninstall_package(application)


"""
Helper classes
"""


class GitRemoteProgress(RemoteProgress):
    """
    An object passed as a callback that will display
    a progressbar while downloading files from the git
    remote
    """

    def __init__(self):
        super().__init__()
        self.progress_bar = None
        self.is_done = False

    def update(self, op_code, cur_count, max_count=None, message=''):
        if self.is_done:
            return

        if self.progress_bar is None:
            self.progress_bar = ProgressBar(max_value=max_count)
            self.progress_bar.start()

        if cur_count == max_count:
            self.progress_bar.finish()
            self.is_done = True
        else:
            self.progress_bar.update(cur_count)


"""
Parsing: Global pydotfiles configs
"""


def get_pydotfiles_config_data_with_override(override_config_local_directory, override_config_remote_repo, cache_directory):
    # Early return: All overrides provided
    if override_config_local_directory is not None and override_config_remote_repo is not None:
        return override_config_local_directory, override_config_remote_repo

    # Applies config-file overrides
    config_local_directory, config_remote_repo = load_pydotfiles_config_data(cache_directory)

    # Adds in the overrides
    if override_config_local_directory is not None:
        config_local_directory = override_config_local_directory

    if override_config_remote_repo is not None:
        config_remote_repo = override_config_remote_repo

    return config_local_directory, config_remote_repo


def load_pydotfiles_config_data(cache_directory):
    """
    Loads in config-file overrides
    if they exist
    """
    config_local_directory = DEFAULT_PYDOTFILES_CONFIG_LOCAL_DIRECTORY
    config_remote_repo = DEFAULT_CONFIG_REMOTE_REPO

    config_data = cache_directory.read_from_config()

    config_file_local_directory = config_data.get('local_directory')
    if config_file_local_directory is not None:
        config_local_directory = config_file_local_directory

    config_file_remote_repo = config_data.get('remote_repo')
    if config_file_remote_repo is not None:
        config_remote_repo = config_file_remote_repo

    return config_local_directory, config_remote_repo


def write_pydotfiles_config_data(cache_directory, config_repo_local, config_repo_remote):
    cache_directory.write_to_config({
        'local_directory': config_repo_local,
        'remote_repo': config_repo_remote
    })


def load_config_repo_remote(config_repo_local):
    config = configparser.ConfigParser()
    config.read_file(open(f'{config_repo_local}/.git/config', 'r'))
    return config["remote \"origin\""]["url"]


"""
Parsing: Module-level configs
"""


def parse_operating_system_config(os_config, cache_directory, directory):
    """
    Deserializes a single OS dictionary
    to an OS object
    """
    if os_config is None:
        return None
    else:
        name = os_config.get('name')
        shell = os_config.get('shell')
        packages = os_config.get('packages')
        applications = os_config.get('applications')

        raw_default_dock = os_config.get('default_dock')
        default_dock_applications = None if raw_default_dock is None else set(raw_default_dock)

        default_settings_file_name = os_config.get('default_settings_file')

        default_settings = None
        if default_settings_file_name is not None:
            default_settings_file_path = os.path.join(directory, default_settings_file_name)
            default_settings = get_os_default_settings(default_settings_file_path)

        return OperatingSystem(
            name=name,
            shell=shell,
            packages=packages,
            applications=applications,
            cache_directory=cache_directory,
            default_dock=default_dock_applications,
            settings=default_settings,
            dock_manager=DockManager(),
        )


def parse_action_configs(action_configs, directory, symlinks, other_files):
    is_sudo_used = False

    if action_configs is None:
        return [], is_sudo_used

    action_map = {}

    for action_group in action_configs:
        action = FileActionType.from_string(action_group.get('action'))
        file_map = action_group.get('files')

        use_sudo = action_group.get('sudo', False)
        make_hidden = action_group.get('hidden', False)
        use_absolute_path = action_group.get('absolute', False)

        if use_sudo:
            is_sudo_used = True

        action_map.update(deserialize_file_action(action, file_map, use_sudo, make_hidden, use_absolute_path, directory, symlinks, other_files))

    return list(action_map.values()), is_sudo_used


"""
Parsing: FileActions
"""


def deserialize_file_action(action, file_map, use_sudo, make_hidden, use_absolute_path, directory, symlinks, other_files):
    action_map = {}

    action_map.update(deserialize_file_action_expansion(action, file_map, use_sudo, make_hidden, symlinks, other_files))

    for origin, destination in file_map.items():
        absolute_origin = resolve_file_action_absolute_origin(action, origin, directory, use_absolute_path)
        absolute_destination = resolve_file_action_absolute_destination(destination, make_hidden)
        action_map[(action, absolute_destination)] = FileAction(action, absolute_origin, absolute_destination, use_sudo)

    return action_map


def deserialize_file_action_expansion(action, file_map, use_sudo, make_hidden, symlinks, other_files):
    action_map = {}

    # Deals with the case of "all"
    all_case_destination_base = file_map.get('*')
    if all_case_destination_base is not None:
        if action == FileActionType.SYMLINK:
            for origin in symlinks:
                destination_file = f"{all_case_destination_base}/{'.' if make_hidden else ''}{os.path.basename(origin).replace('.symlink', '')}"
                absolute_destination = os.path.expanduser(destination_file)
                action_map[(action, absolute_destination)] = FileAction(action, origin, absolute_destination, use_sudo)
        elif action == FileActionType.COPY:
            for origin in other_files:
                destination_file = f"{all_case_destination_base}/{'.' if make_hidden else ''}{os.path.basename(origin)}"
                absolute_destination = os.path.expanduser(destination_file)
                action_map[(action, absolute_destination)] = FileAction(action, origin, absolute_destination, use_sudo)
        else:
            raise NotImplementedError(f"File Action: The file action `{action}` currently doesn't support expansion, please open an issue on github if you would like to have it")
        file_map.pop('*')

    return action_map


def resolve_file_action_absolute_origin(action, origin, directory, use_absolute_path):
    # Early return
    if use_absolute_path:
        return os.path.expanduser(origin)

    # Gives back a relative origin based off of the action type
    if action == FileActionType.SYMLINK:
        return f"{os.path.join(directory, origin)}.symlink"
    elif action == FileActionType.COPY:
        return f"{os.path.join(directory, origin)}"
    else:
        raise NotImplementedError(f"File Action: The action `{action}` is currently not supported")


def resolve_file_action_absolute_destination(destination, make_hidden):
    if make_hidden:
        stripped_file_name = remove_prefix(f"{os.path.basename(destination)}", '.')
        full_file_name = f"{'.' if make_hidden else ''}{stripped_file_name}"
    else:
        full_file_name = os.path.basename(destination)
    destination_directory = os.path.dirname(destination)
    full_destination = os.path.join(destination_directory, full_file_name)

    return os.path.expanduser(full_destination)


"""
Object creation: Modules
"""


def load_active_modules(config_repo_local, active_modules, host_os, cache_directory):
    modules = {}
    is_sudo_used = False

    module_names = get_module_names(config_repo_local) if active_modules is None else active_modules
    for module_name in module_names:
        settings_file = None

        start_file = None
        post_file = None

        undo_start_file = None
        undo_post_file = None

        module_directory = os.path.join(config_repo_local, module_name)
        module_symlinks = []
        module_generic_files = []

        for module_file in os.listdir(module_directory):
            full_module_file_path = os.path.join(module_directory, module_file)
            if module_file == 'start':
                start_file = full_module_file_path
                continue

            if module_file == 'undo-start':
                undo_start_file = full_module_file_path
                continue

            if module_file == 'settings.yaml' or module_file == 'settings.json':
                settings_file = full_module_file_path
                continue

            if module_file == 'post':
                post_file = full_module_file_path
                continue

            if module_file == 'undo-post':
                undo_post_file = full_module_file_path
                continue

            if module_file.endswith(".symlink"):
                module_symlinks.append(full_module_file_path)
            else:
                module_generic_files.append(full_module_file_path)

        modules[module_name] = Module(
            name=module_name,
            directory=module_directory,
            start_file=start_file,
            post_file=post_file,
            undo_start_file=undo_start_file,
            undo_post_file=undo_post_file,
            settings_file=settings_file,
            symlinks=module_symlinks,
            other_files=module_generic_files,
            host_os=host_os,
            cache_directory=cache_directory
        )

        if modules[module_name].is_sudo_used:
            is_sudo_used = True

    return modules, is_sudo_used


def get_module_names(config_repo_local):
    return [module_name for module_name in os.listdir(config_repo_local) if os.path.isdir(os.path.join(config_repo_local, module_name)) and module_name != ".git"]


"""
Helper functions
"""


def run_script(script_file):
    logger.info(f"Script: Running script [File={script_file}]")
    command_result = subprocess.run(script_file)

    if command_result.returncode == 0:
        logger.info(f"Script: Successfully ran script [File={script_file}]")
    else:
        logger.warning(f"Script: Failed to run script [File={script_file}, stderr={command_result.stderr.decode()}")
