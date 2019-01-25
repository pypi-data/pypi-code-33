# -*- coding: utf-8 -*-
"""
Utility functions.
"""

from __future__ import absolute_import, unicode_literals

import os


def find_in_parent_dirs(path, filenames):
    """Searches up from a given path to find files."""
    prev, path = None, os.path.abspath(path)
    while prev != path:
        if any(os.path.exists(os.path.join(path, d)) for d in filenames):
            return path
        prev, path = path, os.path.abspath(os.path.join(path, os.pardir))
    return None


def find_tests_marker(path, markers=(".polarion_tests",)):
    """Searches up from a given path to find the tests markers."""
    return find_in_parent_dirs(path, markers)


def find_vcs_root(path, dirs=(".git",)):
    """Searches up from a given path to find the project root."""
    return find_in_parent_dirs(path, dirs)
