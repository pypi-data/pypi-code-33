"""Console based plugin framework using ArgumentParsers.

This module essentially wraps the argparse module and will provide
methods to add both project specific (internal) and third-party
extensible (external) plugins.
"""

import argparse


class DuplicateParserError(Exception):
    pass


class ParserContainer:
    """Store a parser along with a callback function to handle arg parsing"""

    def __init__(self, parser, target):
        self.parser = parser
        self.target = target

    def __repr__(self):
        return (repr(self.parser)
                + ' | '
                + repr(self.target))

    @property
    def parser(self):
        return self._parser

    @parser.setter
    def parser(self, parser):
        if not isinstance(parser, argparse.ArgumentParser):
            raise TypeError('ArgumentParser expected, not '
                            + type(parser).__name__)
        self._parser = parser

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        if not callable(target):
            raise TypeError('target must be a callable object')
        self._target = target


class ParserStore:
    """Act as a parser generator and store for all created parsers"""

    def __init__(self, in_pkg, ex_path=''):
        """Init"""
        self._set_internal_package(in_pkg)
        self._set_external_path(ex_path)
        self._parser = argparse.ArgumentParser()
        self._subparser = self.parser.add_subparsers(help='Commands')
        self.subparser.required = True
        self.subparser.dest = 'command'
        self._internal = {}
        self._external = {}

    @property
    def parser(self):
        return self._parser

    @property
    def subparser(self):
        return self._subparser

    def set_internal(self, cmd, target, **kwargs):
        parser = self._internal.get(cmd)
        if parser is not None:
            raise DuplicateParserError(cmd + ' is already an internal parser')
        parser = self._subparser.add_parser(cmd, **kwargs)
        self._internal[cmd] = ParserContainer(parser, target)
        self._external.pop(cmd, None)
        #        self._global.pop(cmd, None)
        #        self._local.pop(cmd, None)
        return parser

    def set_external(self, cmd, target, **kwargs):
        parser = self.get_internal(cmd)
        if parser is not None:
            raise DuplicateParserError(cmd + ' is already an internal parser')
        parser = self.get_external(cmd)
        if parser is not None:
            raise DuplicateParserError(cmd + ' is already an external parser')
        parser = self._subparser.add_parser(cmd, **kwargs)
        self._external = ParserContainer(parser, target)
        return parser

    def get_internal(self, cmd, default=None):
        parser = self._internal.get(cmd)
        if parser is not None:
            return parser
        return default

    def get_external(self, cmd, default=None):
        parser = self._external.get(cmd)
        if parser is not None:
            return parser
        return default

    def get(self, cmd, default=None):
        parser = self.get_internal(cmd)
        if parser is not None:
            return parser
        parser = self.get_external(cmd)
        if parser is not None:
            return parser
        return default

    def parse_args(self):
        """Call parser, return parsed args"""
        #        print(_store.parser._subparsers._group_actions[0].choices)
        return self.parser.parse_args()

    def run(self):
        """Pass parsed args to callback function"""
        self._load_internal()
        self._load_external()
        args = self.parse_args()
        command = getattr(args, 'command', None)
        if command is None:
            raise ValueError('no command passed to args')
        parser = self.get(command)
        if parser is None:
            raise RuntimeError('no '
                               + str(command)
                               + ' command handler found')
        parser.target(args)

    def _load_internal(self):
        """Load all default modules in package"""
        package = self._get_internal_package()
        for name in package.__all__:
            module = getattr(package, name, None)
            if module is None:
                raise AttributeError(name
                                     + ' module is not properly imported')
            setup = getattr(module, 'setup', None)
            if setup is None:
                raise AttributeError(name
                                     + ' module is missing a setup function')
            setup()

    def _load_external(self):
        """Load all 'local' modules (merge with global to internal)"""
        path = self._get_external_path()
        if path == '':
            return
        raise NotImplementedError('user plugins is not supported yet')

    def _set_internal_package(self, package):
        all_check = getattr(package, '__all__', None)
        if all_check is None:
            name = getattr(package, '__name__', 'internal package __init__.py')
            raise AttributeError(name +
                                 ' is required to include an __all__ list')
        self._package = package

    def _get_internal_package(self):
        return self._package

    def _set_external_path(self, path):
        if not isinstance(path, str):
            raise TypeError('str expected, not ' + type(path).__name__)
        self._path = path.strip()

    def _get_external_path(self):
        return self._path
