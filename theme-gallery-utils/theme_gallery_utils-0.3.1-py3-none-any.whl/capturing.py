# -*- coding: utf-8 -*-

"""
Module contains methods for capturing theme screenshots.
"""

import logging
import os
import re
import subprocess
import time
from . import paths, xml_utils

logger = logging.getLogger(__name__)


def shutter_args(theme_name, screenshots_dir):
    """Return args to be used to launch shutter."""
    output_file = os.path.join(screenshots_dir, theme_name + ".png")
    args = [
        "shutter",
        "--window=emulationstation",
        "--no_session",
        "--exit_after_capture",
        "--output={}".format(output_file),
    ]
    return args


def emulationstation_args(config, theme_name):
    """Return args to be used to launch emulationstation."""

    # retrieve resolution name if it is defined
    try:
        resolution_name = config["theme_resolutions"][theme_name]
    except KeyError:
        resolution_name = config["defaults"]["resolution"]

    resolution = config["resolutions"][resolution_name]
    width = str(resolution["width"])
    height = str(resolution["height"])

    logger.info("{} at {}x{}".format(theme_name, width, height))

    return [
        "emulationstation",
        "--no-splash",
        "--windowed",
        "--resolution",
        width,
        height,
    ]


def update_es_settings(theme_name, gamelist=False):
    """Update es_config to store the desired theme as default."""
    settings_file = os.path.join(paths.EMULATIONSTATION, "es_settings.cfg")

    # regex pattern for substituting values in es_settings
    settings_regex = r"""
    ("{}"[ ]value=")  # use python substitution for element name, store this
    [^"]*           # match anything but double quote for value
    (")             # match and store closing value quote
    """

    with open(settings_file, "r+") as buf:
        settings_text = buf.read()

        settings_text = re.sub(
            settings_regex.format("ThemeSet"),
            r"\1{}\2".format(theme_name),
            settings_text,
            flags=re.VERBOSE,
        )
        settings_text = re.sub(
            settings_regex.format("StartupSystem"),
            r"\1{}\2".format("atari2600" if gamelist else ""),
            settings_text,
            flags=re.VERBOSE,
        )

        buf.seek(0)
        buf.truncate()
        buf.write(settings_text)


def take_screenshot(config, theme_name, screenshots_dir, gamelist=False):
    """Capture a screenshot of the theme."""

    xml_utils.update_es_systems(config, theme_name)
    update_es_settings(theme_name, gamelist=gamelist)
    es_process = subprocess.Popen(
        emulationstation_args(config, theme_name),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    subprocess.run(
        shutter_args(
            theme_name + "-gamelist" if gamelist else theme_name,
            screenshots_dir,
        ),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    es_process.terminate()


def auto(config, theme_names, screenshots_dir):
    """Capture screenshots for all themes in the list."""

    # ensure screenshots dir exists
    if not os.path.isdir(screenshots_dir):
        os.makedirs(screenshots_dir, exist_ok=True)

    for theme_name in theme_names:
        take_screenshot(config, theme_name, screenshots_dir)
        take_screenshot(config, theme_name, screenshots_dir, gamelist=True)


def install_dependencies(verbose=True):
    """Install shutter as a dependency."""

    args = [
        "sudo",
        "apt-get",
        "install",
        "shutter",
    ]
    kwargs = {"check": True}
    if not verbose:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return subprocess.run(args, **kwargs).returncode
