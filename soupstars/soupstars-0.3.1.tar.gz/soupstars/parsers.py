"""
Parsers
-------

The Parser classes defined here are generally intended to be subclassed, with
user defined instance methods that correspond to a parsed item. The default
loader and reader simply return the arguments passed to their `load` and `read`
methods, so most use cases should use a different loader and reader.

>>> from soupstars import BaseParser
>>> parser = BaseParser(a=1, b=2)
>>> parser.load()  # returns the kwargs passed to BaseParser
{'a': 1, 'b': 2}
>>> parser.read()  # calls parser.load and returns the result
{'a': 1, 'b': 2}

Additionally, you can set a cache on the parser so that expensive load calls
are reduced. The default cache is just an in-memory dictionary, but caches
that use a local filesystem or Redis are available.

>>> parser.cache_id
'ac6dcde3d009f3b5d2ea803c12ef1a3c'
>>> parser.cache.get(parser.cache_id)
{'a': 1, 'b': 2}

Functions on the parsers decorated with `@parse` are considered "parsers" and
treated specially. They can be found by using the `iter_parsers` method.

>>> from soupstars import parse
>>> @parse
... def parse_a(read):
...     return read.get('a')
...
>>> parser.__class__.parse_a = parse_a
>>> parse_a in list(parser.iter_parsers())
True

Those parser functions should typically be accessed by treating the parser
instance like a dictionary.

>>> parser['parse_a']
1
"""

import collections
import doctest
import io
import json
import re

from flask import request, jsonify

from .readers import DefaultReader, HttpReader
from .loaders import DefaultLoader, HttpLoader
from .caches import DefaultCache
from .utils import SoupstarsPlugin


ParserTestResult = collections.namedtuple(
    'ParserTestResult',
    ['failed', 'message', 'parser']
)

ParserNameComponents = collections.namedtuple(
    'ParserNameComponents',
    ['first', 'last', 'classname']
)


class BaseParser(object):
    """
    The primary parsing object. Subclass this to create your own parser.
    """

    loader = DefaultLoader
    reader = DefaultReader
    cache = DefaultCache


    # TODO: use a named tuple, and catch when it's just the BaseParser being
    # used.
    @classmethod
    def __name_components__(klass):
        return re.findall('[A-Z][^A-Z]*', klass.__name__)

    @classmethod
    def iter_parsers(klass):
        """
        Iterate over the parsing functions defined on the parser.
        """

        for attr_name in sorted(dir(klass)):
            attr = getattr(klass, attr_name)
            if hasattr(attr, "__parser__"):
                yield attr

    @classmethod
    def iter_instances(klass, seed_kwargs, generator):
        """
        Generate instances of the parsers

        :param seed_kwargs: kwargs used to initialize the first parser
        :param generator: method to call on the parser to create
        more kwargs used to initialize additional instances. Method should
        accept a single argument with the value of `parser._read()`
        """

        queued_args = [seed_kwargs]
        used_args = []

        while len(queued_args) > 0:
            args = queued_args.pop()
            if args in used_args:
                continue
            parser = klass(**args)
            used_args.append(args)
            generate_func = getattr(klass, generator)
            new_args = generate_func(klass._read(parser))
            queued_args += new_args
            yield parser.dict()


    # TODO: use namedtuple's for the results here.
    @classmethod
    def test(klass):
        """
        Iterates over the doctests defined on a parser, returning tuples of
        (test_result, result_message). For more info see
        https://docs.python.org/2/library/doctest.html#doctestrunner-objects
        """

        doctest_runner = doctest.DocTestRunner()
        doctest_parser = doctest.DocTestParser()
        parser = klass()

        for parser_func in parser.iter_parsers():
            if parser_func.__doc__ is None:
                # We should actually alert that there's no doctest. We need our
                # own "test result" class
                continue
            string = parser_func.__doc__
            globs = {'expected': lambda: parser_func(parser.read())}
            # Shuold name refer to the name of the class here?
            name = parser.__class__.__name__
            # The filename should point to the location of the parser, not this
            # file.
            filename = __file__
            # This would be really nice. Maybe we can detect via string
            # matching?
            lineno = None
            test = doctest_parser.get_doctest(string, globs, name, filename,
                                              lineno)
            out = io.StringIO()
            test_result = doctest_runner.run(test, out=out.write)
            message = out.getvalue()
            failed = test_result.failed > 0
            yield  ParserTestResult(failed=failed, message=message,
                                    parser=parser.__class__)

    def __init__(self, lazy=False, **load_args):
        self._init_plugins()
        self.load_args = load_args
        self.all_params = self.plugin_args()
        self.all_params.update(self.load_args)
        self.cache_id = self.cache.hash_id(self.loader, **self.all_params)
        if not lazy:
            self._load()

    def __getitem__(self, key):
        for parser in self.__class__.iter_parsers():
            if parser.__name__ == key:
                return parser.__call__(self._read())
        else:
            raise KeyError

    def plugins(self):
        """
        Any class on the parser that subclasses SoupstarsPlugin is a plugin
        """

        plugins = {}
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            try:
                if issubclass(attr, SoupstarsPlugin):
                    plugins[attr_name] = attr
            except TypeError:
                pass
        else:
            return plugins


    def plugin_args(self):
        """
        Any ALL_CAPS class attribute on the parser is considered a plugin
        argument
        """

        plugin_args = {}
        for attr_name in dir(self.__class__):
            if attr_name == attr_name.upper():
                attr = getattr(self.__class__, attr_name)
                plugin_args[attr_name] = attr
        else:
            return plugin_args

    def _init_plugins(self):
        for plugin_name, plugin in self.plugins().items():
            default_plugin_args = plugin.default_args().copy()
            for arg in default_plugin_args:
                if arg in self.plugin_args():
                    default_plugin_args[arg] = self.plugin_args()[arg]
            setattr(self, plugin_name, plugin(**default_plugin_args))

    def _load(self):
        return self.cache.get(self.cache_id) \
               or self.cache.update(self.cache_id, self.loader, **self.load_args)

    def _read(self):
        return self.reader.read(self._load())

    def load(self):
        """
        Load the data to parser.
        """

        return self._load()

    def read(self):
        """
        Read the loaded data.
        """

        return self._read()

    def items(self):
        """
        Iterate over (parser_name, parse_result) values
        """

        for parser in self.__class__.iter_parsers():
            yield parser.__name__, parser.__call__(self._read())

    def dict(self):
        """
        Convert the (parser_name, parse_result) tuples to a dictionary.
        """

        return dict(self.items())

    def json(self, indent=0):
        """
        Convert the parser dictionary to json.
        """

        return json.dumps(self.dict(), indent=indent)


class HttpParser(BaseParser):
    """
    :var HOST: The default host to use, defaults to `http://0.0.0.0`
    :var ROUTE: The default route to use, defaults to `/`
    """


    # Note that default host should not end in a /
    HOST = "http://0.0.0.0"
    ROUTE = "/"

    loader = HttpLoader
    reader = HttpReader
