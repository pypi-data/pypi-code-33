# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Customized data structures"""
from .exceptions import CodedValueError


class TolerantDict(dict):
    """A mapping that is tolerant to the type
    of the key, in associated queries.

    :param class cast: The expected type of the
        keys.
    :param str emsg: Message to display in
        case of a casting error.
    """
    def __init__(self, *args, cast=int, emsg=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cast = cast
        self.emsg = emsg

    def __getitem__(self, key):
        try:
            return super().__getitem__(self.cast(key))
        except Exception:
            raise CodedValueError(1005, self.emsg)
