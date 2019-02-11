from .magic import magic_get_dict, magic_flush_mro_cache
from .common import get_best

def get_fuzzy(self, key, default=None, level=0.75):
    if key in self:
        return self.get(key, default)
    
    best_key = get_best(self, key, level)
    if best_key:
        return self.get(best_key)
    return default

dct = magic_get_dict(dict)
dct['get_fuzzy'] = get_fuzzy

magic_flush_mro_cache()
