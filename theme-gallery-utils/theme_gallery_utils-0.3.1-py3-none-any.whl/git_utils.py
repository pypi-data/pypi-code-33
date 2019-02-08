# -*- coding: utf-8 -*-

"""
Module contains git related utilities.
"""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def pull_dir(theme_dir, verbose=True):
    """Pull any changes to the given repo dir."""
    logger.info("Pulling {}".format(theme_dir))

    args = ["git", "pull"]
    kwargs = {"cwd": theme_dir}
    if not verbose:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    process = subprocess.run(args, **kwargs)

    return process.returncode


def clone_theme(theme, themes_dir, verbose=True):
    """Clone a theme from github to the given base directory."""
    logger.info("Cloning {}".format(theme))

    user, repo = theme
    short_name = repo.replace("es-theme-", "")

    url = "https://github.com/{}/{}".format(user, repo)

    args = ["git", "clone", "--depth=1", url, short_name]
    kwargs = {"cwd": themes_dir}
    if not verbose:
        kwargs.update(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    process = subprocess.run(args, **kwargs)

    return process.returncode


def pull_or_clone(theme, themes_dir, verbose=True):
    """Execute a pull or clone on a given theme."""

    # ensure directory exists
    os.makedirs(themes_dir, exist_ok=True)

    user, repo = theme
    short_name = repo.replace("es-theme-", "")

    # if the theme directory already exists, pull it
    theme_dir = os.path.join(themes_dir, short_name)
    if os.path.isdir(theme_dir):
        return_code = pull_dir(theme_dir, verbose=verbose)

    # if the directory doesn't exist clone it
    else:
        return_code = clone_theme(theme, themes_dir, verbose=verbose)

    return return_code
