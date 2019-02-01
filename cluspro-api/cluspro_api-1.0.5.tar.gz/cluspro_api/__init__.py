from __future__ import absolute_import
import logging

import hmac as _hmac
import hashlib as _hashlib

from .config import get_config
from .version import version

__version__ = version

CONFIG = get_config()

logging.getLogger(__name__).addHandler(logging.NullHandler())

def make_sig(form, secret):
    sig = ""
    for k in sorted(form.keys()):
        if form[k] is not None:
            sig += "{}{}".format(k, form[k])
    return _hmac.new(
        secret.encode('utf-8'), sig.encode('utf-8'), _hashlib.md5).hexdigest()
