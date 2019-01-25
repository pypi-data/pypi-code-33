# -*- coding: utf-8 -*-
# pylint: disable=useless-object-inheritance
"""
Checks Polarion docstrings using flake8.
"""

from __future__ import absolute_import, unicode_literals

from pkg_resources import get_distribution

from polarion_docstrings import checker, configuration


def get_version():
    """Returns plugin version."""
    try:
        # __package__ is not in python 2.7
        return get_distribution(__name__.split(".")[0]).version
    # pylint: disable=broad-except
    except Exception:
        # package is not installed
        return "0.0"


def set_compiled_lists(config):
    """Saves compiled regular expressions for whitelist and blacklist into config."""
    if not config:
        return
    config["_compiled_whitelist"], config[
        "_compiled_blacklist"
    ] = checker.DocstringsChecker.get_compiled_lists(config)


class PolarionDocstringsPlugin(object):
    """The flake8 entry point."""

    name = "polarion_checks"
    version = get_version()
    config = None

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        self.set_config(filename)

    @classmethod
    def set_config(cls, filename):
        """Sets plugin configuration.

        We set it once as a class attribute so the setup doesn't need to be done
        repeatedly for each checked file.
        """
        if cls.config is None:
            cls.config = configuration.get_config(project_path=filename) or {}
            set_compiled_lists(cls.config)

    def run(self):
        """Runs checks."""
        return checker.DocstringsChecker(
            self.tree, self.filename, self.config, PolarionDocstringsPlugin
        ).get_errors()
