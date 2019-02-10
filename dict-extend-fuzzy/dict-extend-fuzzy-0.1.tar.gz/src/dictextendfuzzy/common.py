from difflib import get_close_matches

def transform(key):
    return str(key).lower()

def get_best(dict_, key, level):
    if key is None:
        key = ''

    mapping = { transform(k):k for k in dict_.keys() } 
    keys = mapping.keys()

    best_keys = get_close_matches(transform(key), keys, n=1, cutoff=level)
    if best_keys:
        return mapping.get(best_keys[0])
    return None
