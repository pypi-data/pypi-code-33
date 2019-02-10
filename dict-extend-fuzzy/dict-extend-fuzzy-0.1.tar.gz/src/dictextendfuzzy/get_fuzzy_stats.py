from difflib import SequenceMatcher
from collections import namedtuple

from .magic import magic_get_dict, magic_flush_mro_cache
from .common import get_best, transform

def get_fuzzy_stats(self, key, default=None, level=0.75):
    obj = namedtuple('d', ('ratio', 'key', 'value'))
    if key in self:
        return obj(
            key=key,
            value=self.get(key),
            ratio=1.0
        )
    
    best_key = get_best(self, key, level)
    if best_key:
                
        return obj(
            key=best_key,
            value=self.get(best_key),
            ratio=SequenceMatcher(None, transform(best_key), transform(key)).ratio()
        )

    return obj(
        key=None,
        value=default,
        ratio=0
    )

dct = magic_get_dict(dict)
dct['get_fuzzy_stats'] = get_fuzzy_stats

magic_flush_mro_cache()
