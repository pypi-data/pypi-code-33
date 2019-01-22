"""
TODO:
    - ls command (parsers under home, examples, etc)
    - open command (for finding parsers)
    - create command
    - parse command
        - pass additional command line args to parser's init (ie to loader)
    - test command
        - prettier formatting of test results
        - named tuples for test results
    - search command
        - do some scanning for specific words in the `read` object
    - show command
        - describe the parsing functions on the parser
"""

import datetime as dt
import inspect
import os
import re

import click
from click import echo, style

from .utils import iter_parsers


LOGGING_STRING = "{ts} [{level}] {text}"


def info(text):
    level = style("INF", fg="blue", bold=True)
    ts = style(str(dt.datetime.now().time()), fg="bright_white", bold=True)
    echo(LOGGING_STRING.format(level=level, text=text, ts=ts))


def success(text):
    level = style("SUC", fg="green", bold=True)
    ts = style(str(dt.datetime.now().time()), fg="bright_white", bold=True)
    echo(LOGGING_STRING.format(level=level, text=text, ts=ts))


def fail(text):
    level = style("ERR", fg="red", bold=True)
    ts = style(str(dt.datetime.now().time()), fg="bright_white", bold=True)
    echo(LOGGING_STRING.format(level=level, text=text, ts=ts))


@click.group()
def main():
    pass


@main.command()
def ls():
    """
    List all available parsers
    """

    for Parser in iter_parsers():
        name = Parser.__name__
        parser_type = style(Parser.__base__.__name__.split('.')[-1], fg="cyan", bold=True)
        location = Parser.__module__
        text = "\t".join([name, parser_type, location])
        info(text)

# The arguments here should be optional filters to apply to the name of
# the parser. By default `soupstars test` should run tests on all parsers.
@main.command()
@click.argument('scope')
@click.argument('name')
def test(scope, name):
    """
    Test the `@parse` methods from a parser using its docstrings
    """

    for Parser in iter_parsers():
        name_components = [s.lower() for s in re.findall('[A-Z][^A-Z]*', Parser.__name__)]
        pscope, pname, _parser_str = name_components
        if pscope == scope.lower() and pname == name.lower():
            for test_result in Parser().test():
                if test_result.failed:
                    fail("Failed")
                    fail(test_result.message)
                else:
                    success("Passed")


@main.command()
@click.argument('scope')
@click.argument('name')
def parse(scope, name):
    """
    Run a parser
    """
    for Parser in iter_parsers():
        name_components = [s.lower() for s in re.findall('[A-Z][^A-Z]*', Parser.__name__)]
        pscope, pname, _parser_str = name_components
        if pscope == scope.lower() and pname == name.lower():
            info(f"Running {Parser.__name__}")
            success("Received: \n" + Parser().json(indent=2))


@main.command()
def dirs():
    """
    List directories with parsers
    """

    # print('tset')
    from soupstars.utils import iter_parser_directories
    for dir_ in iter_parser_directories():
        info(str(dir_))


@main.command()
def packages():
    """
    List packages with parsers
    """

    # print('tset')
    from soupstars.utils import iter_package_paths
    for pp in iter_package_paths():
        info(str(pp))


@main.command()
def modules():
    """
    List the modules searched for parsers
    """

    from soupstars.utils import iter_parser_modules
    for pp in iter_parser_modules():
        info(str(pp))


@main.command()
@click.argument('package')
@click.argument('module')
def create(package, module):
    """
    Create a new parser in the soupstars home directory
    """

    from soupstars import SoupstarsConfig
    config = SoupstarsConfig()

    parser_template = """from soupstars import HttpParser, parse, FilesystemCache

class {package}{module}Parser(HttpParser):

    cache = FilesystemCache
    HOST = "https://www.facebook.com"
    ROUTE = "/"

    @parse
    def title(soup):
        \"\"\"
        >>> expected()
        "My title"
        \"\"\"
        return soup.find('h1')

    """.format(package=package.capitalize(), module=module.capitalize())

    package_path = os.path.join(config.SOUPSTARS_HOME, package)
    module_path = os.path.join(package_path, module) + '.py'
    try:
        os.mkdir(package_path)
    except FileExistsError:
        pass


    f = open(os.path.join(package_path, '__init__.py'), 'w+')
    f.write('"test"')
    f.close()

    try:
        with open(module_path, 'w') as f:
            f.write(parser_template)
    except Exception:
        fail("Failed")
