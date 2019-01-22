#
# copyright (c) 2019 east301
#
# This software is released under the Apache License, Version 2.0.
# https://opensource.org/licenses/Apache-2.0
#

import os


def get_request_meta_as_dict(request):
    result = {}
    for key, value in request.META.items():
        if (not key.startswith('wsgi.')) and (key not in os.environ):
            result[key] = value

    return result
