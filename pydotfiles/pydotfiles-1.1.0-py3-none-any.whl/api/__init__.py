# General imports
import argparse
import pydotfiles
import os

# Project imports
from pydotfiles.models import PYDOTFILES_CACHE_DIRECTORY, DEFAULT_PYDOTFILES_CONFIG_LOCAL_DIRECTORY, DEFAULT_CONFIG_REMOTE_REPO
from pydotfiles.models import Dotfiles, CacheDirectory, Validator
from pydotfiles.models import get_pydotfiles_config_data_with_override, load_pydotfiles_config_data, write_pydotfiles_config_data
from pydotfiles.models import PydotfilesError
from pydotfiles.utils import PrettyPrint


class ArgumentDispatcher:
    """
    A presentation-layer class to contain all logic around
    using the pydotfiles API, providing help menus and
    simplifying argument-parsing via dynamic dispatching
    of commands
    """

    def __init__(self, api_arguments):
        self.dotfiles = None
        self.api_arguments = api_arguments

    def dispatch(self):
        valid_commands = [
            'download',
            'install',
            'uninstall',
            'update',
            'clean',
            'set',
            'validate',
        ]

        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="""
        Python Dotfiles Manager, enabling configuration-based management of your system!

        Commands:
          - download: Downloads your dotfiles onto your computer
          - install: Installs all/part of your dotfiles
          - uninstall: Uninstalls all/part of your dotfiles
          - update: Updates all/part of your dotfiles
          - clean: Removes the pydotfiles cache/default
          - set: Sets configuration values for managing your dotfiles
          - validate: Validates that a given directory is pydotfiles-compliant
        """)
        parser.add_argument('--version', action='version', version='%(prog)s ' + pydotfiles.__version__)
        parser.add_argument("command", help="Runs the command given", choices=valid_commands)

        command = self.api_arguments[1:2]
        command_arguments = self.api_arguments[2:]

        args = parser.parse_args(command)

        # Dynamically dispatches to the relevant method
        getattr(self, args.command)(command_arguments)

    def download(self, command_arguments):
        help_description = f"""
        Downloads the dotfiles config repo if it hasn't been cloned to local.

        Pydotfiles's configuration is setup in a fallthrough manner:
            - Command-line arguments passed in override all other configs, and will be persisted in $HOME/.pydotfiles/config.json
            - Any non-overridden arguments is then configured from: $HOME/.pydotfiles/config.json (if it exists)
            - Any remaining arguments will default to:
                - Local directory: {DEFAULT_PYDOTFILES_CONFIG_LOCAL_DIRECTORY}
                - Remote repo: {DEFAULT_CONFIG_REMOTE_REPO}
        """
        parser = self.__get_base_parser(help_description, "download")
        parser.add_argument("-l", "--local-directory", help="The local directory where the dotfiles are stored")
        parser.add_argument("-r", "--remote-repo", help="The local directory where the dotfiles are stored")
        args = parser.parse_args(command_arguments)

        # TODO P4: Add in cleaner signature
        config_repo_local, config_repo_remote = get_pydotfiles_config_data_with_override(args.local_directory, args.remote_repo, CacheDirectory())

        self.dotfiles = Dotfiles(config_repo_local, config_repo_remote, args.quiet, args.verbose)

        if self.dotfiles.is_cloned:
            PrettyPrint.success(f"Clone: Dotfiles have already been cloned")
            return

        try:
            self.dotfiles.download()
        except PydotfilesError as e:
            PrettyPrint.fail(e.help_message)

    def install(self, command_arguments):
        help_description = """
        Installs your dotfile's modules (default: installs all modules)
        NOTE: Your dotfiles need to have first been downloaded via `pydotfiles download` beforehand
        """
        parser = self.__get_base_parser(help_description, "install")
        parser.add_argument("-m", "--modules", help="A list of specific modules to install", nargs="+")
        args = parser.parse_args(command_arguments)

        # TODO P4: Add in cleaner signature
        config_repo_local, config_repo_remote = load_pydotfiles_config_data(CacheDirectory())

        self.dotfiles = Dotfiles(config_repo_local, config_repo_remote, args.quiet, args.verbose, args.modules)

        if not self.dotfiles.is_cloned:
            PrettyPrint.fail(f"Install: No dotfiles detected, please download it first with `pydotfiles download`")

        if args.modules is None:
            self.dotfiles.install_all()
        else:
            self.dotfiles.install_multiple_modules(args.modules)

    def uninstall(self, command_arguments):
        help_description = """
        Uninstalls your dotfile's modules (default: uninstalls all modules, but leaves packages, applications, and dev-environments alone)
        """
        parser = self.__get_base_parser(help_description, "uninstall")
        parser.add_argument("-m", "--modules", help="A list of specific modules to uninstall", nargs="+")
        parser.add_argument("-p", "--uninstall-packages", help="Will uninstall all packages installed with these module(s)", action="store_true")
        parser.add_argument("-a", "--uninstall-applications", help="Will uninstall all applications installed with these module(s)", action="store_true")
        parser.add_argument("-e", "--uninstall-environments", help="Will uninstall all dev environments with these module(s)", action="store_true")
        args = parser.parse_args(command_arguments)

        config_repo_local, config_repo_remote = load_pydotfiles_config_data(CacheDirectory())

        PrettyPrint.info(f"Uninstall: Uninstalling dotfiles")

        self.dotfiles = Dotfiles(config_repo_local, config_repo_remote, args.quiet, args.verbose, args.modules)

        if not self.dotfiles.is_cloned:
            PrettyPrint.fail(f"Uninstall: Could not uninstall- no dotfiles detected")

        if args.modules is None:
            self.dotfiles.uninstall_all(args.uninstall_packages, args.uninstall_applications, args.uninstall_environments)
        else:
            self.dotfiles.uninstall_multiple_modules(args.modules, args.uninstall_packages, args.uninstall_applications, args.uninstall_environments)

    def update(self, command_arguments):
        help_description = """
        Updates the local dotfiles from the remote repo
        """
        parser = self.__get_base_parser(help_description, "update")
        args = parser.parse_args(command_arguments)

        config_repo_local, config_repo_remote = load_pydotfiles_config_data(CacheDirectory())

        self.dotfiles = Dotfiles(config_repo_local, config_repo_remote, args.quiet, args.verbose)

        if not self.dotfiles.is_cloned:
            PrettyPrint.fail(f"Update: Could not update- no dotfiles detected")

        self.dotfiles.update()

    def clean(self, command_arguments):
        help_description = f"""
        Deletes either the pydotfiles cache or the downloaded local dotfiles config repo

        Possible choices:
            - cache: Deletes everything in the pydotfiles cache directory ({os.path.expanduser(PYDOTFILES_CACHE_DIRECTORY)})
            - repo: Deletes everything in the locally downloaded dotfiles configuration directory ({DEFAULT_PYDOTFILES_CONFIG_LOCAL_DIRECTORY})
        """
        valid_cleaning_targets = ['cache', 'repo']
        parser = self.__get_base_parser(help_description, "clean")
        parser.add_argument('clean_target', help='Clears out the given cleaning target', choices=valid_cleaning_targets)
        args = parser.parse_args(command_arguments)

        config_repo_local, config_repo_remote = load_pydotfiles_config_data(CacheDirectory())

        self.dotfiles = Dotfiles(config_repo_local, config_repo_remote, args.quiet, args.verbose)

        self.dotfiles.clean(args.clean_target)

    def set(self, command_arguments):
        help_description = f"""
        Enables direct setting of pydotfile config values
        """
        parser = self.__get_base_parser(help_description, "set")
        parser.add_argument("-l", "--local-directory", help="Sets the dotfiles configuration repo to a different local directory")
        parser.add_argument("-r", "--remote-repo", help="Sets pydotfiles to point to a different remote repo")
        args = parser.parse_args(command_arguments)

        cache_directory = CacheDirectory()

        config_repo_local, config_repo_remote = load_pydotfiles_config_data(cache_directory)

        if args.local_directory is not None:
            config_repo_local = args.local_directory

        if args.remote_repo is not None:
            config_repo_remote = args.remote_repo

        write_pydotfiles_config_data(cache_directory, config_repo_local, config_repo_remote)
        PrettyPrint.success(f"Set: Successfully persisted configuration data [local-directory={config_repo_local}, remote-repo={config_repo_remote}]")

    def validate(self, command_arguments):
        help_description = """
        Validates a given directory and whether it's pydotfiles-compliant.
        (default: Checks the current working directory)
        """
        parser = self.__get_base_parser(help_description, "validate")
        parser.add_argument("-d", "--directory", help="Validates the passed in directory", default=os.getcwd())

        args = parser.parse_args(command_arguments)

        validator = Validator(args.quiet, args.verbose)
        try:
            validator.validate_directory(args.directory)
        except PydotfilesError as e:
            PrettyPrint.fail(e.help_message)

    @staticmethod
    def __get_base_parser(description, sub_command):
        parser = argparse.ArgumentParser(
            prog=f"pydotfiles {sub_command}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=description
        )
        logging_parser_group = parser.add_mutually_exclusive_group()
        logging_parser_group.add_argument("-v", "--verbose", help="Enables more verbose logging", action="store_true")
        logging_parser_group.add_argument("-q", "--quiet", help="Squelches the default logging (still outputs to stderr upon failures)", action="store_true")
        return parser
