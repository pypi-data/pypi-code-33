# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import tempfile
from typing import Union, List, Tuple

import virtualenv

from pytesting_utils.preconditions import Preconditions


class VirtualEnvironment(object):
    """
    Wraps a virtual environment.

    This class should not be used directly, as you need to call `cleanup()`
    manually in order to remove the create temporary files.
    Better use the `virtualenv` context manager.
    """

    def __init__(
        self, env_name: str, tmp_dir: Union[bytes, str, os.PathLike] = None
    ) -> None:
        """
        Creates a new virtual environment in a temporary folder.

        :param env_name: Name of the virtual environment
        :param tmp_dir: Directory where the temporary folder should be created
        """
        Preconditions.check_argument(
            len(env_name) > 0,
            "Cannot create an virtual environment without a name!",
        )
        self._env_name = env_name
        self._packages = []

        self._env_dir = tempfile.mkdtemp(suffix=env_name, dir=tmp_dir)
        virtualenv.create_environment(self._env_dir)

    def cleanup(self) -> None:
        """Cleans up the virtual environment"""
        shutil.rmtree(self._env_dir)

    def get_env_dir(self) -> Union[bytes, str, os.PathLike]:
        """
        Give the temporary folder the virtual environment is installed in.

        :return: The path to the virtual environment folder
        """
        return self._env_dir

    def add_package_for_installation(self, package: str) -> None:
        """
        Add a package to the list of PyPI packages that will be installed
        before the execution.

        :param package: The name of a package on PyPI
        """
        self._packages.append(package)

    def add_packages_for_installation(self, packages: List[str]) -> None:
        """
        Adds a list of packages to the list of PyPI packages that will be
        installed before the execution.

        :param packages: A list of package names on PyPI
        """
        self._packages.extend(packages)

    def run_commands(self, commands: List[str]) -> Tuple[str, str]:
        """
        Run commands in the virtual environment setting.

        ATTENTION: Be careful, the commands will be run in a sub-process and
        can be used for possible security flaws!  Be sure that you know what
        you do, when executing stuff here!

        :param commands: A list of commands the be executed in the virtual env
        :return: A tuple of output and error outputs of the process
        """
        command_list = [
            "source {}".format(os.path.join(self._env_dir, "bin", "activate")),
            "python -V",
        ]
        for package in self._packages:
            command_list.append("pip install {}".format(package))
        command_list.extend(commands)
        cmd = ";".join(command_list)
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        out, err = process.communicate()
        return out.decode("utf-8"), err.decode("utf-8")

    def __str__(self) -> str:
        return "VirtualEnvironment {} in directory {}".format(
            self._env_name, self._env_dir
        )

    def __repr__(self) -> str:
        return self.__str__()
