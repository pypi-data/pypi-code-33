"""This module defines the Jupyter inspection magic commands."""
import inspect
import sys

from pygments import highlight
from pygments.lexers import RstLexer, Python3Lexer
from pygments.formatters import HtmlFormatter

from IPython.core.magic import Magics, magics_class, line_magic
from IPython.core.magic_arguments import (magic_arguments, argument,
                                          parse_argstring)
from IPython.display import HTML


@magics_class
class InspectMagics(Magics):
    @line_magic
    @magic_arguments()
    @argument('--doc', '-d', action='store_true',
              help='Return only the documented help for an object')
    @argument('--module', '-m', action='store_true',
              help='Return module associated with an object')
    @argument('--path', '-p', action='store_true',
              help='Return path for the file in which an object is defined')
    @argument('object', help='The object to inspect')
    def inspect(self, line='', cell=None):
        args = parse_argstring(self.inspect, line)
        if args.doc:
            return self.doc(line.lstrip('-d ').lstrip('--doc '))
        elif args.path:
            return self.module_path(line.lstrip('-p').lstrip('--path'))
        elif args.module:
            return self.module(line.lstrip('-m').lstrip('--module'))
        return self.source(line)

    @line_magic
    def doc(self, line):
        obj = eval(line)  # quick and dirty - sorry!
        docstring = inspect.getdoc(obj)
        return HTML(highlight(docstring, RstLexer(),
                              HtmlFormatter(full=True)))

    @line_magic
    def module(self, line):
        try:
            obj = eval(line)  # quick and dirty - sorry!
            return obj.__module__
        except AttributeError:
            try:
                return obj.__package__
            except AttributeError:
                print('Unable to establish module for: {!r}'.format(obj),
                      file=sys.stderr)
        except TypeError as err:
            print('{}: {!r}'.format(err.__class__.__name__, str(err)),
                  file=sys.stderr)

    @line_magic
    def module_path(self, line):
        try:
            return inspect.getfile(eval(line))  # quick and dirty - sorry!
        except TypeError as err:
            print('{}: {!r}'.format(err.__class__.__name__, str(err)),
                  file=sys.stderr)

    @line_magic
    def source(self, line):
        try:
            obj = eval(line)  # quick and dirty - sorry!
            return HTML(highlight(inspect.getsource(obj),
                                  Python3Lexer(), HtmlFormatter(full=True)))
        except TypeError as err:
            print('{}: {!r}'.format(err.__class__.__name__, str(err)),
                  file=sys.stderr)
