from collections import OrderedDict
from copy import deepcopy
from hashlib import md5
import os


def ua_hash(user_agent):
    """
    Return short hash of User Agent string for 
    memory-efficient cache key.
    """
    return md5(user_agent.encode('utf-8')).hexdigest()[:9]


# interpolate regex with anchors so
# iPhone / Tiphone are matched correctly
BOUNDED_REGEX = r'(?:^|[^A-Z0-9_\-])(?:{})'
MAX_CACHE_SIZE = 384


class LRUDict(OrderedDict):
    """
    An dict that can discard least-recently-used items via maximum capacity.

    An item is considered "used" by direct access via [] or get() only,
    not via iterating over the whole collection with items(), for example.

    Expired entries only get purged after insertions or changes, or by
    manually calling purge().
    """

    def __init__(self, *args, maxkeys=MAX_CACHE_SIZE, **kwargs):
        """
        Same arguments as OrderedDict with 1 addition

        maxkeys: maximum number of keys being kept.
        """
        super().__init__(*args, **kwargs)
        self.maxkeys = maxkeys
        self.purge()

    def purge(self):
        """
        Pop least used keys until maximum keys is reached.
        """
        overflowing = max(0, len(self) - self.maxkeys)
        for _ in range(overflowing):
            self.popitem(last=False)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        try:
            self.move_to_end(key)
        except KeyError:
            pass
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.purge()


class Cache(dict):

    base = {
        'regexes': {},
        'normalize_regexes': [],
        'user_agents': LRUDict(),
    }

    def __init__(self, *args, **kwargs):
        kwargs.update(deepcopy(self.base))
        super().__init__(*args, **kwargs)

    def clear(self):
        super().clear()
        self.update(deepcopy(self.base))


ROOT = os.path.dirname(os.path.abspath(__file__))

DDCache = Cache()

WORTHLESS_UA_TYPES = {
    'UUID',
    'Numeric',
    'Gibberish',
}


__all__ = (
    'BOUNDED_REGEX',
    'DDCache',
    'LRUDict',
    'ROOT',
    'WORTHLESS_UA_TYPES',
    'ua_hash',
)

