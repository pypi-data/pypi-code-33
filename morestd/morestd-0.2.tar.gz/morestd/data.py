#
# morestd: More standard libraries for Python
#
# Copyright 2010-2018 Ferry Boender, released under the MIT license
#

"""
Various tools and helpers to work with standard data structures.
"""

import copy


def to_bool(s):
    """
    Convert string `s` into a boolean.

    `s` can be 'true', 'True', 1, 'false', 'False', 0.

    Examples:

    >>> to_bool("true")
    True
    >>> to_bool("0")
    False
    >>> to_bool(True)
    True
    """
    if isinstance(s, bool):
        return s
    elif s.lower() in ['true', '1']:
        return True
    elif s.lower() in ['false', '0']:
        return False
    else:
        raise ValueError("Can't cast '%s' to bool" % (s))


def deepupdate(target, src, overwrite=True):
    """Deep update target list, dict or set or other iterable with src
    For each k,v in src: if k doesn't exist in target, it is deep copied from
    src to target. Otherwise, if v is a list, target[k] is extended with
    src[k]. If v is a set, target[k] is updated with v, If v is a dict,
    recursively deep-update it. If `overwrite` is False, existing values in
    target will not be overwritten.

    Examples:
    >>> t = {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi']}
    >>> deepupdate(t, {'hobbies': ['gaming']})
    >>> t
    {'name': 'Ferry', 'hobbies': ['programming', 'sci-fi', 'gaming']}
    """
    for k, v in src.items():
        if type(v) == list:
            if k not in target:
                target[k] = copy.deepcopy(v)
            elif overwrite is True:
                target[k].extend(v)
        elif type(v) == dict:
            if k not in target:
                target[k] = copy.deepcopy(v)
            else:
                deepupdate(target[k], v, overwrite=overwrite)
        elif type(v) == set:
            if k not in target:
                target[k] = v.copy()
            elif overwrite is True:
                if type(target[k]) == list:
                    target[k].extend(v)
                elif type(target[k]) == set:
                    target[k].update(v)
                else:
                    raise TypeError("Cannot update {} with {}".format(
                        type(target[k]),
                        type(v))
                    )
        else:
            if k not in target or overwrite is True:
                target[k] = copy.copy(v)


# Empty object who's id we'll use as a 'no default given' placeholder for the
# `get` method
_get_no_default = object()


class _Get:
    def __init__(self, data, default):
        self.data = data
        self.default = default
        self.pointer = data

    def _get(self, k):
        if self.pointer is self.default:
            return self

        try:
            self.pointer = self.pointer[k]
        except (IndexError, KeyError):
            if self.default is not _get_no_default:
                self.pointer = self.default
            else:
                raise

        return self

    def __getattr__(self, attr):
        return self._get(attr)

    def __getitem__(self, key):
        return self._get(key)

    def expr(self, expr):
        escape = False
        cur_token = ''

        for c in expr:
            if escape is True:
                cur_token += c
                escape = False
            else:
                if c == '\\':
                    # Next char will be escaped
                    escape = True
                    continue
                elif c == '[':
                    # Next token is of type index (list)
                    if len(cur_token) > 0:
                        self._get(cur_token)
                        cur_token = ''
                elif c == ']':
                    # End of index token. Next token defaults to a key (dict)
                    if len(cur_token) > 0:
                        self._get(int(cur_token))
                        cur_token = ''
                elif c == '.':
                    # End of key token. Next token defaults to a key (dict)
                    if len(cur_token) > 0:
                        self._get(cur_token)
                        cur_token = ''
                else:
                    # Append char to token name
                    cur_token += c

        if len(cur_token) > 0:
            self._get(cur_token)

        return self

    def val(self):
        return self.pointer


def get(data, default=_get_no_default):
    """
    Easily access deeply nested data structures without having to test for
    key and index availability at each level.

    This turns code such as:

        try:
          return d.getdefault("feed", {}).getdefault("tags", [])[0]
        except IndexError:
          return "default value"

    into:

        return get(d, "default_value").feed.tags[0].val()

    Examples:

    >>> d = {
    ...   'feed': {
    ...     'id': 'my_feed',
    ...     'url': 'http://example.com/feed.rss',
    ...     'tags': ['devel', 'example', 'python'],
    ...     'short.desc': 'A feed',
    ...     'list': [
    ...       {
    ...         'uuid': 'e9b48a2'
    ...       }
    ...     ]
    ...   }
    ... }

    # Get value
    >>> get(d).feed.tags[-1].val()
    'python'

    >>> get(d).feed.list[0].uuid.val()
    'e9b48a2'

    # Return default if path is not found
    >>> get(d, "default.ico").feed.icon.val()
    'default.ico'

    # Access paths with special chars in them
    >>> get(d).feed["short.desc"].val()
    'A feed'

    # Use a string expression to access data
    >>> get(d).expr("feed.short\\.desc").val()
    'A feed'

    >>> get(d).expr("feed.list[0].uuid").val()
    'e9b48a2'
    """
    return(_Get(data, default))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
