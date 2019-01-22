"""
Loaders
-------

The loader classes are intended to interface with other systems, and are
created by subclassing the `BaseLoader` class. A loader should expose a
`load` method, which is generally used by the `Cache` objects whenever
it can't find an object it has already stored.

In the simplest case, the `DefaultLoader` just returns the arguments it
receives.

>>> from soupstars import DefaultLoader
>>> loader = DefaultLoader()
>>> loader.load(a=1, b=2)
{'a': 1, 'b': 2}

The `HttpLoader` will pull data from a website. The class attributes
`default_route` and `default_host` are used to control how the loader builds
its requests.

>>> loader = HttpLoader()
>>> loader.ROUTE
'/photos/1'
>>> from minimock import Mock
>>> requests.get = Mock("requests.get")
>>> requests.get.mock_returns = "result"
>>> loader.load()
Called requests.get('https://jsonplaceholder.typicode.com/photos/1')
'result'
>>> requests.get.mock_returns = "result2"
>>> loader.load(url='https://www.google.com/search?')
Called requests.get('https://www.google.com/search?')
'result2'
>>> requests.get.mock_returns = "result3"
>>> loader.load(route="/photos/2")
Called requests.get('https://jsonplaceholder.typicode.com/photos/2')
'result3'

"""

import requests

from .exceptions import NotImplementedError
from .utils import SoupstarsPlugin


class BaseLoader(SoupstarsPlugin):
    """
    Base loader. Subclass this to create your own loader.
    """

    def load(self, **kwargs):
        raise NotImplementedError


class DefaultLoader(BaseLoader):
    """
    Default loader, returns the keyword arguments passed to `load`.
    """

    def load(self, **kwargs):
        return kwargs


class HttpLoader(BaseLoader):
    """
    Uses requests.get to load a webpage.
    """

    HOST = "https://jsonplaceholder.typicode.com"
    ROUTE = "/photos/1"

    # Move the doctests into the module docstring
    def load(self, **kwargs):
        if 'url' not in kwargs and 'route' not in kwargs:
            return requests.get(self.HOST + self.ROUTE, **kwargs)
        elif 'url' in kwargs:
            url = kwargs.pop('url')
            return requests.get(url, **kwargs)
        elif 'route' in kwargs:
            route = kwargs.pop('route')
            return requests.get(self.HOST + route, **kwargs)
        else:
            raise AttributeError("Unexpected argument handling")
