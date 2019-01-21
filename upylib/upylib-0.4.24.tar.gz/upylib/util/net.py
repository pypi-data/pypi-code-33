#!/usr/bin/env python3
# -*- coding:utf-8 -*-⏎

from __future__ import print_function
import sys

if sys.version_info<(3,0,0):
    reload(sys)
    sys.setdefaultencoding('utf8')


import urllib.request
import urllib.parse
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
def read_url(url, retry=1, encoding="utf-8", verbose=1):
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
    if not url:
        if verbose >= 1:
            print("no url")
        return False

    for _ in range(0,retry):
        try:
            c = urllib.request.urlopen(url)
            content = c.read()
            if encoding:
                content = content.decode(encoding)
            return content

        except Exception as e:
            if verbose >= 1:
                print(e)
            continue

    return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
def get_url(url, retry=1, encoding="utf-8", verbose=1):
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
    return read_url(url, retry, encoding, verbose)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
def post_url(url, retry=1, data_byte=None, data_dict=None, encoding="utf-8", verbose=1):
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
    if not url:
        if verbose >= 1:
            print("no url")
        return False

    for _ in range(0,retry):
        try:
            if data_byte:
                data = data_byte
            elif data_dict:
                data = urllib.parse.urlencode( data_dict ).encode("ascii")
            else:
                data = None

            c = urllib.request.urlopen(url=url, data=data)
            content = c.read()
            if encoding:
                content = content.decode(encoding)
            return content

        except Exception as e:
            if verbose >= 1:
                print(e)
            continue

    return False



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
def urlenc(q):
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
    return urllib.parse.quote_plus(q)

