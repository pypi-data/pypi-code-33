from __future__ import unicode_literals
import logging
from urlparse import urljoin
import const

log = logging.getLogger(__name__)


def get_url(subpath, api_url=None):
    if not api_url:
        api_url = const.API
    return api_url + subpath

