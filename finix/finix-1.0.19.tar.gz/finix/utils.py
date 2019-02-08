from __future__ import unicode_literals
import re
from . import wac_config


def to_uri(href):
    result = href
    if href is not None and href.startswith(wac_config.root_url):
        result = re.sub(("%s:*\d*(.*)" % wac_config.root_url), r"\1", result)
        result = "/" + "/".join(filter(None, result.split("/")))

    return result
