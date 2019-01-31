from pluckit.pluckit import pluckit


def rekey(obj, key_handle, value_handle = None):
    if obj is None:
        # nothing to rekey
        return None

    if key_handle is None and value_handle is None:
        # nothing to do, so bail
        return obj

    # validate input type
    supported_types = [ list, dict, set, tuple ]
    if not any([ isinstance(obj, t) for t in supported_types ]):
        # last chance, try casting to a list
        try:
            obj = list(obj)
        except TypeError:
            raise TypeError(
                'type not supported: %s' % obj.__class__
            )

    # determine return type
    if key_handle or hasattr(obj, 'keys'):
        res = {}
    else:
        res = []

    # determine how to iterate and unpack items
    if hasattr(obj, 'keys'):
        _iter = obj.items()
        kv_fn = lambda items: items
    else:
        _iter = obj
        # no key, only value
        kv_fn = lambda items: (None, items)

    # rekey
    for items in _iter:
        # unpack key / value tuple
        key, value = kv_fn(items)

        # set default result values
        new_key, new_value = key, value

        # grab new key / value
        if key_handle != None:
            new_key = pluckit(value, key_handle)

        if value_handle != None:
            new_value = pluckit(value, value_handle)

        # store results
        if type(res) == list:
            res.append(new_value)
        else:
            res[new_key] = new_value

    return res
