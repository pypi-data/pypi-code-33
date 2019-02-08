# -*- coding: utf-8 -*-

"""Top-level package for django-ignorebots."""

__author__ = """Alister Cordiner"""
__email__ = 'acordiner@gmail.com'
__version__ = '0.1.0'


import re

ADMIN_URLS = [re.compile(url) for url in [
    r'^/axis2/axis2-admin/login$',
]]

BITCOIN_URLS = [re.compile(url) for url in [
    r'/wallet\.dat$',
    r'^(/backup)?/\.?bitcoin/.*$',
]]

WORDPRESS_URLS = [re.compile(url) for url in [
    r'^/xmlrpc\.php.*$',
    r'/wp-(content|includes|admin)/.*$',
    r'/wp-login\.php$',
]]

ALL_URLS = ADMIN_URLS + BITCOIN_URLS + WORDPRESS_URLS
