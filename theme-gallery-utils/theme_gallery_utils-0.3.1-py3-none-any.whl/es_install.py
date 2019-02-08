# -*- coding: utf-8 -*-

"""
Module contains methods to install and configure emulationstation environment.
"""

import logging
import os
import shutil
import subprocess
from . import paths

logger = logging.getLogger(__name__)


def install_dependencies(verbose=True):
    """Install emulationstation dependencies."""
    dependencies = [
        "libsdl2-dev",
        "libfreeimage-dev",
        "libfreetype6-dev",
        "libcurl4-openssl-dev",
        "libasound2-dev",
        "libgl1-mesa-dev",
        "build-essential",
        "cmake",
        "fonts-droid-fallback",
        "libvlc-dev",
        "libvlccore-dev",
        "vlc-bin",
        "libcec-dev",  # unofficially
        "libp8-platform-dev",  # unofficially
        "rapidjson-dev",  # unofficially
    ]
    install_args = ["sudo", "apt-get", "install"]
    mark_args = ["sudo", "apt-mark", "auto"]
    kwargs = {"check": True}
    if not verbose:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # install the packages
    process = subprocess.run(install_args + dependencies, **kwargs)

    # if they were installed properly, mark them as auto
    if process.returncode == 0:
        dependencies.remove("build-essential")
        dependencies.remove("cmake")
        dependencies.remove("libfreeimage-dev")

        subprocess.run(mark_args + dependencies, **kwargs)

    return process.returncode


def clone(es_dir, verbose=True):
    """Clone emulationstation."""
    args = [
        "git",
        "clone",
        "--recursive",
        "--depth=1",
        "https://github.com/Retropie/EmulationStation",
        es_dir,
    ]
    kwargs = {"check": True}
    if not verbose:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return subprocess.run(args, **kwargs).returncode


def build(build_dir, verbose=True):
    """Build emulationstation."""
    kwargs = {"cwd": build_dir, "check": True}
    if not verbose:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run(["cmake", "."], **kwargs)
    return subprocess.run(["make", "-j4"], **kwargs).returncode


def configure(es_dir):
    """Apply config files and sample files to emulationstation."""

    # copy over es_systems
    shutil.copy(
        os.path.join(paths.RESOURCES, "es_systems.cfg"),
        es_dir,
    )

    # copy over all sample directories
    for dir_name in ("downloaded_images/", "gamelists/", "roms/"):
        source = os.path.join(paths.RESOURCES, dir_name)
        destination = os.path.join(es_dir, dir_name)
        if os.path.isdir(destination):
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
