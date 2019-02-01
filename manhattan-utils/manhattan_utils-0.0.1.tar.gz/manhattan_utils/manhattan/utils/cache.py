from functools import lru_cache

from flask import url_for

__all__ = [
    'caching_url_for'
]


@lru_cache(maxsize=2560)
def caching_url_for(endpoint, **values):
    """A version of `url_for` that caches the output"""
    return url_for(endpoint, **values)
