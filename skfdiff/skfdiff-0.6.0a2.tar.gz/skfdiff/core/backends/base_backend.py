#!/usr/bin/env python
# coding=utf-8

from abc import ABC

import attr
from fuzzywuzzy import process

from ..grid_builder import GridBuilder
from ..system import PDESys

available_backends = {}


def get_backend(name):
    """get a backend by its name

    Arguments:
        name {str} -- backend name

    Raises:
        NotImplementedError -- raised if the backend is not available.

    Returns:
        Backend -- the requested backend
    """
    try:
        return available_backends[name]
    except KeyError:
        err_msg = "%s backend is not registered." % name
        (suggest, score), = process.extract(name, available_backends.keys(), limit=1)
        if score > 70:
            err_msg += (
                "\n%s is available and seems to be close. "
                "It may be what you are looking for !" % suggest
            )
        err_msg += "\nFull list of available backends:\n\t- %s" % (
            "\n\t- ".join(available_backends.keys())
        )
        raise NotImplementedError(err_msg)


def register_backend(CustomBackend):
    global available_backends
    if Backend not in CustomBackend.__mro__:
        raise AttributeError(
            "The provider backend should inherit from the " "Backend base class."
        )
    available_backends[CustomBackend.name] = CustomBackend


@attr.s
class Backend(ABC):
    system = attr.ib(type=PDESys)
    grid_builder = attr.ib(type=GridBuilder)
