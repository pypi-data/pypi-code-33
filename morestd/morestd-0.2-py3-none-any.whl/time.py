#
# morestd: More standard libraries for Python
#
# Copyright 2010-2018 Ferry Boender, released under the MIT license
#

from datetime import datetime, timedelta


def duration(secs):
    """
    Return a human-readable representation of elapsed time.

    Examples:

    >>> duration(4)
    '4s'
    >>> duration(456)
    '7m 36s'
    >>> duration(4567)
    '1h 16m'
    >>> duration(45678)
    '12h 41m'
    >>> duration(456789)
    '5d 6h'
    >>> duration(3456789)
    '9d 13m'
    >>> duration(23456789)
    '28d 11h'
    """

    sec = timedelta(seconds=int(secs))
    d = datetime(1, 1, 1) + sec
    k = ["%dd", "%dh", "%dm", "%ds"]
    v = [d.day-1, d.hour, d.minute, d.second]
    t = [k[i] % (v[i]) for i in range(len(k)) if v[i] > 0]
    return ' '.join(t[:2])


if __name__ == '__main__':
    import doctest
    doctest.testmod()
