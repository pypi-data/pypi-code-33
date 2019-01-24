"""
Utils
-----

Utility functions are used for retrieving all known parser classes, and provide
methods for integrating with a flask app.

>>> from soupstars.examples import NytimesArticleParser
>>> parser_classes = list(iter_parsers())
>>> parser_classes[0]
<class 'bible.verses.BibleVersesParser'>
"""

import importlib
import os
import sys

from flask import Blueprint, Flask

from .config import SoupstarsConfig


config = SoupstarsConfig()


class SoupstarsPlugin(object):

    @classmethod
    def default_args(klass):
        args = {}
        for attr in dir(klass):
            if attr == attr.upper():
                args[attr] = getattr(klass, attr)
        else:
            return args

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def iter_parser_directories():
    parser_directories = [config.SOUPSTARS_HOME]

    if config.SOUPSTARS_LOAD_EXAMPLES:
        parser_directories.append(config.SOUPSTARS_EXAMPLES_PATH)

    for pd in parser_directories:
        yield pd


# TODO: rename to `iter_parser_package_paths`
def iter_package_paths():
    for package_dir in iter_parser_directories():
        package_dir_items = os.listdir(package_dir)
        for item in package_dir_items:
            if item == "__pycache__" or item == "__init__.py":
                continue

            item_path = os.path.join(package_dir, item)
            if os.path.isdir(item_path) and "__init__.py" in os.listdir(item_path):
                yield item_path


def iter_parser_modules():
    for path in iter_package_paths():
        modules = os.listdir(path)
        for module in modules:
            if module not in ("__pycache__", "__init__.py"):
                yield os.path.join(path, module)


# TODO: rename to `iter_parser_classes`
def iter_parsers():
    """
    Iterate over all the parsers, optionally excluding example parsers
    if `SOUPSTARS_LOAD_EXAMPLES` is `False`.
    """

    # I think we can just add the directory containg the package to the
    # sys.path, and then import the parser from there
    for filename in iter_parser_modules():
        components = filename.split(os.path.sep)
        module = components.pop()
        module_name = module.split(".")[0]
        package_name = components.pop()
        parser_relative_directory = os.path.sep.join(components)
        # This means users can only import their examples by pulling directly
        # from soupstars.iter_parsers, `from my_example import X` won't work
        if parser_relative_directory not in sys.path:
            sys.path.append(parser_relative_directory)

        classname = "{pn}{mn}Parser".format(
            pn=package_name.capitalize(),
            mn=module_name.capitalize()
        )

        parser_import_path = ".".join([package_name, module_name])
        module = importlib.import_module(parser_import_path)
        parser = getattr(module, classname)
        yield parser


def parse(func):
    """
    Decorate an instance method of a parser to indicate the function should be
    used when calling methods like `Parser.json()`
    """

    func.__parser__ = True
    return func
