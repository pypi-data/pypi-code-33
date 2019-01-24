"""
Readers
-------

Readers are responsible for taking an object returned by a `Loader` and
transforming it into an object ready for parsing. They can be thought of as
a function that gets "shared" by all `@parse` methods of a `Parser`.

>>> from soupstars import DefaultReader
>>> reader = DefaultReader()
>>> reader.read({'a': 1, 'b': 2})
{'a': 1, 'b': 2}

The `HttpReader` converts a `requests.Response` object into a `bs4.BeautifulSoup`
object.

>>> from unittest.mock import MagicMock
>>> resp = MagicMock()
>>> resp.content = b'<h1>Hello world!</h2>'
...
>>> from soupstars import HttpReader
>>> reader = HttpReader()
>>> reader.read(resp).h1.text
'Hello world!'
"""

import bs4

from .exceptions import NotImplementedError
from .utils import SoupstarsPlugin


# Would also be nice if readers supported a "search" function to scan thru
# their loads.
class BaseReader(SoupstarsPlugin):
    """
    The base reader. Subclass this to create a custom reader.
    """

    def read(self, load):
        raise NotImplementedError


class DefaultReader(BaseReader):
    """
    The default reader. Simply returns the single argument passed to `read`.
    """

    def read(self, load):
        return load


class HttpReader(BaseReader):
    """
    A reader for converting a `requests.Response` object into a
    `bs4.BeautifulSoup` object.
    """

    def read(self, resp):
        return bs4.BeautifulSoup(resp.content.decode('utf8'), features="html.parser")
