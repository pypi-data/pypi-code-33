# -*- coding: utf8 -*-
import click
from missinglink.core.default_params import get_default


def option_with_default_factory(param_name, **kwargs):
    default_key = kwargs.pop('default_key', None)
    if default_key is not None:
        kwargs['default'] = get_default(default_key)

    return click.option(param_name, **kwargs)
