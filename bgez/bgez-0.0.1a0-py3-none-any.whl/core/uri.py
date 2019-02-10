from typing import Any, Union, Mapping, List

import urllib.parse

__all__ = [
    'URI', 'Query',
]

class URI:
    '''
    Wrapper around `urllib.parse.ParseResult`:
    - scheme: (`file`, `http`, `https`, ...)
    - authority: (`localhost`, `192.168.0.1`, `www.google.com`, ...)
    - path: (`/path/to/resource`, ...)
    - params: (...)
    - query: special object `Query` (`?a=1&b=2`, ...)
    - fragment: (`#link`, ...)

    Adds some utility methods to compare the URI and change values.
    See `help(URI)`.
    '''

    __slots__ = ('__weakref__',
        'scheme', 'authority', 'path', 'params', '__query', 'fragment')

    def __init__(self, path: Any = '', **kargs):
        (
            self.scheme,
            self.authority,
            self.path,
            self.params,
            self.query,
            self.fragment,
        ) = urllib.parse.urlparse(path)
        self.update(**kargs)

    @property
    def query(self) -> str:
        return self.__query

    @query.setter
    def query(self, query) -> None:
        if not isinstance(query, Query):
            query = Query(query)
        self.__query = query

    def update(self, **kargs):
        for key, value in kargs.items():
            setattr(self, key, value)

    def copy(self, **kargs):
        uri = type(self)()
        uri.scheme = kargs.get('scheme', self.scheme)
        uri.authority = kargs.get('authority', self.authority)
        uri.path = kargs.get('path', self.path)
        uri.params = kargs.get('params', self.params)
        uri.query = kargs.get('query', self.query)
        uri.fragment = kargs.get('fragment', self.fragment)
        return uri

    def __str__(self):
        return urllib.parse.urlunparse(self)
    s = property(__str__) # shortcut: `uri.s`

    def __iter__(self):
        return iter((
            self.scheme, self.authority, self.path,
            self.params, str(self.query), self.fragment
        ))

class Query:
    '''
    Query object to simplify edition of such arguments.
    '''

    __slots__ = ('__weakref__', '__query', '__dict')

    def __init__(self, query: str):
        self.__dict = dict()
        if isinstance(query, str):
            query = urllib.parse.parse_qs(query)
        elif isinstance(query, list):
            query = self.__query_list_to_dict(query)
        elif not isinstance(query, dict):
            raise ValueError(f'wrong type {type(query)}')
        self.__dict.update(query)

    def __query_list_to_dict(self, keyValueList: list) -> dict:
        query = dict()
        for key, value in keyValueList:
            query.setdefault(key, []).append(value)
        return query

    def __query_dict_to_list(self, keyValuesDict: dict) -> list:
        return [(key, value)
            for key, values in keyValuesDict.items()
            for value in values]

    def __query_encode(self) -> str:
        return urllib.parse.urlencode(
            self.__query_dict_to_list(self.__dict))

    def has(self, key: str):
        return len(self.__dict.get(key, [])) > 0
    __contains__ = has

    def add(self, key: str, *values) -> None:
        self.__dict.setdefault(key, []).extend(values)

    def remove(self, key: str) -> None:
        self.__dict.pop(key, ...)

    def getall(self, key: str) -> list:
        return self.__dict.get(key, [])

    def get(self, key: str, index: int = 0, *, type: type = lambda x: x) -> Any:
        try:
            value = self.getall(key)[index]
        except LookupError:
            return None
        return type(value)

    def __str__(self) -> str:
        return self.__query_encode()
    s = property(__str__) # shortcut: `uri.s`

    def __repr__(self) -> str:
        cls = type(self)
        return f'{cls.__module__}.{cls.__qualname__}({str(self)})'

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)
