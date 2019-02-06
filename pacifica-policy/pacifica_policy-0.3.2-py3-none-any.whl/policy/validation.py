#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Validation methods for various objects."""
from __future__ import absolute_import
import re
from functools import wraps
import cherrypy
from .globals import MATCH_VALIDATORS


def validate_user(index=0):
    """Validate the user id."""
    return validate_universal(index, 'user')


def validate_transaction(index=0):
    """Validate the transaction id."""
    return validate_universal(index, 'transaction')


def validate_proposal(index=0):
    """Validate the proposal id."""
    return validate_universal(index, 'proposal')


def _get_check_id(index, *args, **kwargs):
    """Return the check ID in args or kwargs."""
    try:
        return args[int(index)]
    except ValueError:
        return kwargs[str(index)]


def validate_universal(index, regex):
    """Decorator generator to validate proposal field."""
    def decorator(func):
        """Wrapped decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapped function."""
            check_id = _get_check_id(index, *args, **kwargs)
            if not re.match(MATCH_VALIDATORS[regex], check_id):
                message = 'Provide an appropriate {0}_id value'.format(regex)
                raise cherrypy.HTTPError(
                    '400 Invalid Request', message)
            return func(*args, **kwargs)
        return wrapper
    return decorator
