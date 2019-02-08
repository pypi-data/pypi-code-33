#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified file path handling module.
"""

import os


HOME = os.path.expanduser("~")

# base project dir is one level up from paths module
BASE = os.path.abspath(os.path.dirname(__file__))

# resources directory holds non-code files included in package
RESOURCES = os.path.join(BASE, "resources/")

# cache dir used for log files
CACHE = os.path.join(
    os.getenv("XDG_CACHE_HOME", os.path.join(HOME, ".cache/")),
    "gallery_utils/",
)


# data dir used for output
DATA = os.path.join(
    os.getenv("XDG_DATA_HOME", os.path.join(HOME, ".local/share/")),
    "gallery_utils/",
)

BIN = os.path.join(HOME, "bin")

# data subdirectories
UNCOMPRESSED = os.path.join(DATA, "uncompressed/")
COMPRESSED = os.path.join(DATA, "compressed/")
DIFFERENCES = os.path.join(DATA, "differences/")

# theme install location
EMULATIONSTATION = os.path.join(HOME, ".emulationstation")
ESTHEMES = os.path.join(EMULATIONSTATION, "themes/")

# gallery location
GALLERY = os.path.join(HOME, "projects/es-theme-gallery")


def configure_paths(config):
    """Update default paths if specified in config file."""

    key_map = {
        "bin": BIN,
        "emulationstation": EMULATIONSTATION,
        "gallery": GALLERY,
        "log_output": CACHE,
        "output": DATA,
        "themes": ESTHEMES,
    }

    # update the global variables if they are defined in the config
    for key in key_map:
        try:
            key_map[key] = config[key]
        except KeyError:
            pass


if __name__ == "__main__":
    pass
