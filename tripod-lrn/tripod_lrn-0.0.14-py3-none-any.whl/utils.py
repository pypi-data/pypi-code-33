# -*- coding: utf-8 -*-
"""
Utils Manager module. 
Defines utility functions that helps to manage the Flask application and BluePrints

"""
from importlib import import_module
import importlib
import sys
import os
import six
import inspect
import pkgutil


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    if '.' not in dotted_path:
        return import_module(dotted_path)
    else:

        try:
            module_path, class_name = dotted_path.rsplit('.', 1)
        except ValueError:
            msg = "%s doesn't look like a module path" % dotted_path
            six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

        module = import_module(module_path)

        try:
            return getattr(module, class_name)
        except AttributeError:
            msg = 'Module "{}" does not define a "{}" attribute/class'.format(
                dotted_path, class_name
            )
            six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])


def check_module_existence(dotted_path):
    """
    Returns true if the module exists and false otherwise.
    :param dotted_path: module dotted_path string.
    """
    try:
        spam_spec = importlib.util.find_spec(dotted_path)
        found = spam_spec is not None
        return found
    except ImportError:
        return False


def auto_discover(module_selector, member_selector, package_path):
    """
    simple module and member auto discovery function.
    :param member_selector: a selector function to a module members.
    :param module_selector: a module filter function.
    :param package_path: dotted path to the root pack
    :return: yields tuples of (module, mod_members).
    """
    # recursively scan the package
    for finder, name, is_pack in pkgutil.walk_packages(path=[package_path]):
        if is_pack:
            continue

        if module_selector(finder, name, is_pack):
            mod = finder.find_module(name).load_module(name)
            # filter mercury members
            mod_members = inspect.getmembers(
                mod,
                predicate=member_selector
            )
            yield mod, mod_members


def is_package(mod):
    """
    returns true if a given module is a package. False otherwise.
    :param mod: an imported module
    """
    if not hasattr(mod, "__path__"):
        return False
    path = mod.__path__[0]
    if os.path.isdir(path):
        if os.path.isfile(path+"/__init__.py"):
            return True

    return False
