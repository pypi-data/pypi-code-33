#
# copyright (c) 2019 east301
#
# This software is released under the Apache License, Version 2.0.
# https://opensource.org/licenses/Apache-2.0
#

import os
import re

from django.conf import settings
from django.http import HttpResponse

try:
    from css_html_js_minify import html_minify
except ImportError:
    html_minify = None


# ================================================================================
# middleware
# ================================================================================

class HtmlMinifyMiddleware(object):
    def __init__(self, get_response):
        if html_minify is None:
            raise ImportError('css_html_js_minify not found.')

        self.get_response = get_response
        self.enabled = getattr(settings, 'HTML_MINIFY', False)

    def __call__(self, request):
        #
        response = self.get_response(request)
        if (not self.enabled) or (not isinstance(response, HttpResponse)):
            return response

        content_type = response.get('Content-Type')
        if not content_type.startswith('text/html'):
            return response

        #
        match = re.search('charset=([a-zA-Z0-9_\-]+)', content_type)
        charset = match.group(1) if match else 'utf-8'

        try:
            body = response.content.decode(charset)
            body = html_minify(body)
            response.content = body.encode(charset)
        except:     # NOQA
            pass    # ignore errors

        return response


# ================================================================================
# context processor
# ================================================================================

def django_settings(request):
    return {
        'django_settings': settings
    }
