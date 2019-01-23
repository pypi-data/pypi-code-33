# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Sanitizer used to remove sensitive data from our payload"""

import re

from .utils import is_string, is_unicode

SENSITIVE_KEYS = {
    'password', 'secret', 'passwd', 'authorization', 'api_key', 'apikey', 'access_token'
}
MASK = '<Redacted by Sqreen>'
# Strip data which look likes credit card
REGEX = re.compile(r'^(?:\d[ -]*?){13,16}$')


def strip_sensitive_data(data):
    """Sanitize sensitive data from an object"""
    if is_string(data):
        if not is_unicode(data):
            data = data.decode("utf-8", errors="replace")

        if REGEX.match(data):
            return MASK
        return data

    if isinstance(data, dict):
        sanitize_data = {}
        for k, v in data.items():
            if k in SENSITIVE_KEYS:
                sanitize_data[k] = MASK
            else:
                sanitize_data[k] = strip_sensitive_data(v)

        return sanitize_data

    if isinstance(data, (list, tuple, set)):
        return [strip_sensitive_data(v) for v in data]

    return data
