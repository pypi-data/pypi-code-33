import sys
from collections import Iterable
from past.builtins import basestring
basestr = basestring
def urlopen(url):
    if sys.version_info[0] == 3:
        import urllib.request as urllib
    else:
        import urllib
    result = urllib.urlopen(url)
    return result.getcode()


if sys.version_info[0]==3:
    from .oas_metabase_py3 import OASMetaBase
else:
    from .oas_metabase_py2 import OASMetaBase

