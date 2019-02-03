# -*- coding: utf-8 -*-
from os import path
from os import environ
from .parse import parse as _parse
from .coerce import coerce as _coerce
from .inherit import inherit as _inherit
from .readonly import ReadOnlyDict


def read_config(config_input):
    '''
    read_config assumes `config_input` is one of the following in this
    order:

        1. a file path string.
        2. an environment variable name.
        3. a raw config string.

    '''
    def _readlines(pth):
        with open(pth, 'r') as fh_:
            return fh_.read()

    if path.exists(config_input):
        config_input = _readlines(config_input)

    elif config_input in environ and path.exists(environ[config_input]):
        config_input = _readlines(environ[config_input])

    return config_input.split('\n')


def load(config_path, **kwargs):
    #  inheritance=False, readonly=True, use_pathlib=False, use_decimal=False, coercers=None):

    config = _parse(read_config(config_path))

    use_pathlib = kwargs.get('use_pathlib', False)
    use_decimal = kwargs.get('use_decimal', False)
    coercers = kwargs.get('coercers')

    config = _coerce(config, pathlib=use_pathlib, decimal=use_decimal, coercers=coercers)

    if kwargs.get('inheritance', False) is True:
        config = _inherit(config)

    if kwargs.get('readonly', True) is True:
        config = ReadOnlyDict(config)

    return config
