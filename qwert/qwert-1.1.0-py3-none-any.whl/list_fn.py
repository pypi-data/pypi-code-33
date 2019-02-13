#!/usr/bin/env python
# encoding: utf-8


def unique(source: list):
    """
    Unique.

    :param list source: Source list
    :return: list
    """
    r = []
    for el in source:
        if el not in r:
            r.append(el)
    return r


def strip(source: list):
    """
    Strip.

    :param list source: Source list
    :return: list
    """
    r = []
    for value in source:
        if isinstance(value, str):
            r.append(value.strip())
        else:
            r.append(value)
    return r


def remove(source: list, els=None):
    """
    Remove elements.

    :param list source: Source list
    :param els: Element(s) to be removed
    :return: list
    """
    r = []
    if els is None:
        els = ['', None]
    elif not isinstance(els, list):
        els = [els]

    for el in source:
        if el not in els:
            r.append(el)

    return r


def strip_and_unique(source: list):
    """
    Strip and unique.

    :param list source: Source list
    :return: list
    """
    r = unique(strip(source=source))
    return r


def strip_and_remove(source: list, els=None):
    """
    Strip and remove.

    :param list source: Source list
    :param els: Element(s) to be removed
    :return: list
    """
    r = remove(strip(source=source), els=els)
    return r


def remove_and_unique(source: list, els=None):
    """
    Remove and unique.

    :param list source: Source list
    :param els: Element(s) to be removed
    :return: list
    """
    r = unique(remove(source=source, els=els))
    return r


def sur(source: list, els=None):
    """
    Strip, unique, remove.

    :param list source: Source list
    :param els: Element(s) to be removed
    :return: list
    """
    r = remove(strip_and_unique(source=source), els=els)
    return r
