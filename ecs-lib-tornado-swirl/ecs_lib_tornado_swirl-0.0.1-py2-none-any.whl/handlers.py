# -*- coding: utf-8 -*-
"""
Swagger handler utils
"""

from tornado.web import StaticFileHandler, URLSpec

from tornado_swirl.views import (SwaggerApiHandler, #SwaggerResourcesHandler,
                                 SwaggerUIHandler)

import tornado_swirl.settings as settings
import os
__author__ = 'rduldulao'


def swagger_handlers():
    """Returns the swagger UI handlers

    Returns:
        [(route, handler)] -- list of Tornado URLSpec
    """

    prefix = settings.default_settings.get('swagger_prefix', '/swagger')
    if prefix[-1] != '/':
        prefix += '/'
    # Le o arquivo
    #
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # print(dir_path)
    # index = open(dir_path + "/index.html", "r").read()
    # # Muda o prefixo
    # index.replace('{{prefix}}', prefix)
    # # Salva no outro local
    # # open(dir_path + "/static/index.html", "w").write(index)

    return [
        URLSpec(prefix + r'spec.html$', SwaggerUIHandler,
                settings.default_settings, name=settings.URL_SWAGGER_API_DOCS),
        URLSpec(prefix + r'spec$', SwaggerApiHandler,
                name=settings.URL_SWAGGER_API_SPEC),
        (prefix + r'(.*\.(css|png|gif|js))', StaticFileHandler,
         {'path': settings.default_settings.get('static_path')}),
    ]
