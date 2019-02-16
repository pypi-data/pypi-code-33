#!/usr/bin/env python
# encoding: utf-8


def get_dict_by_keys(source, keys: list or dict, default_none: bool = True):
    """
    Get a dict, by keys.

    :param source:
        dict, json_string, or a object
    :param keys:
        list, or dict when there is expecting default values for keys
    :param bool default_none:
        Available only if keys is a list
        Set the default value is None, or ignore it, when the value does not exist
    :return:
        dict
    """
    r = dict()

    # dict
    if isinstance(source, dict):
        if isinstance(keys, list):
            for _key in keys:
                if _key in source.keys():
                    r[_key] = source[_key]
                else:
                    if default_none:
                        r[_key] = None
        elif isinstance(keys, dict):
            for _key, value in keys.items():
                if _key in source.keys():
                    r[_key] = source[_key]
                else:
                    r[_key] = value

    # json_string
    elif isinstance(source, str):
        try:
            import json
            source = json.loads(source)
        except:
            return r

        return get_dict_by_keys(source, keys=keys, default_none=default_none)

    # object
    else:
        if isinstance(keys, list):
            for _key in keys:
                if default_none:
                    r[_key] = getattr(source, _key, None)
                elif hasattr(source, _key):
                    r[_key] = getattr(source, _key)
        elif isinstance(keys, dict):
            for _key, value in keys.items():
                r[_key] = getattr(source, _key, value)

    return r
