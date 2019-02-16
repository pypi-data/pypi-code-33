# -*- coding: utf-8 -*-
# This file is part of the pycalver project
# https://github.com/mbarkhau/pycalver
#
# Copyright (c) 2018 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
"""Compose Regular Expressions from Patterns.

>>> version_info = PYCALVER_RE.match("v201712.0123-alpha").groupdict()
>>> assert version_info == {
...     "pycalver"    : "v201712.0123-alpha",
...     "vYYYYMM"     : "v201712",
...     "year"        : "2017",
...     "month"       : "12",
...     "build"       : ".0123",
...     "build_no"    : "0123",
...     "release"     : "-alpha",
...     "release_tag" : "alpha",
... }
>>>
>>> version_info = PYCALVER_RE.match("v201712.0033").groupdict()
>>> assert version_info == {
...     "pycalver"   : "v201712.0033",
...     "vYYYYMM"    : "v201712",
...     "year"       : "2017",
...     "month"      : "12",
...     "build"      : ".0033",
...     "build_no"   : "0033",
...     "release"    : None,
...     "release_tag": None,
... }
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import re
import typing as typ
PYCALVER_PATTERN = """
\\b
(?P<pycalver>
    (?P<vYYYYMM>
       v                        # "v" version prefix
       (?P<year>\\d{4})
       (?P<month>\\d{2})
    )
    (?P<build>
        \\.                      # "." build nr prefix
        (?P<build_no>\\d{4,})
    )
    (?P<release>
        \\-                      # "-" release prefix
        (?P<release_tag>alpha|beta|dev|rc|post)
    )?
)(?:\\s|$)
"""
PYCALVER_RE = re.compile(PYCALVER_PATTERN, flags=re.VERBOSE)
PATTERN_ESCAPES = [('\\', '\\\\'), ('-', '\\-'), ('.', '\\.'), ('+', '\\+'),
    ('*', '\\*'), ('{', '\\{'), ('}', '\\}'), ('[', '\\['), (']', '\\]'), (
    '(', '\\('), (')', '\\)')]
COMPOSITE_PART_PATTERNS = {'pep440_pycalver':
    '{year}{month}\\.{BID}(?:{pep440_tag})?', 'pycalver':
    'v{year}{month}\\.{bid}(?:-{tag})?', 'calver': 'v{year}{month}',
    'semver': '{MAJOR}\\.{MINOR}\\.{PATCH}', 'release_tag': '{tag}',
    'build': '\\.{bid}', 'release': '-{tag}', 'pep440_version':
    '{year}{month}\\.{BID}(?:{pep440_tag})?'}
PART_PATTERNS = {'year': '\\d{4}', 'month': '(?:0[0-9]|1[0-2])', 'build_no':
    '\\d{4,}', 'pep440_tag': '(?:a|b|dev|rc|post)?\\d*', 'tag':
    '(?:alpha|beta|dev|rc|post|final)', 'yy': '\\d{2}', 'yyyy': '\\d{4}',
    'quarter': '[1-4]', 'iso_week': '(?:[0-4]\\d|5[0-3])', 'us_week':
    '(?:[0-4]\\d|5[0-3])', 'dom': '(0[1-9]|[1-2][0-9]|3[0-1])', 'doy':
    '(?:[0-2]\\d\\d|3[0-5][0-9]|36[0-6])', 'MAJOR': '\\d+', 'MINOR': '\\d+',
    'MM': '\\d{2,}', 'MMM': '\\d{3,}', 'MMMM': '\\d{4,}', 'MMMMM':
    '\\d{5,}', 'PATCH': '\\d+', 'PP': '\\d{2,}', 'PPP': '\\d{3,}', 'PPPP':
    '\\d{4,}', 'PPPPP': '\\d{5,}', 'bid': '\\d{4,}', 'BID': '[1-9]\\d*',
    'BB': '[1-9]\\d{1,}', 'BBB': '[1-9]\\d{2,}', 'BBBB': '[1-9]\\d{3,}',
    'BBBBB': '[1-9]\\d{4,}', 'BBBBBB': '[1-9]\\d{5,}', 'BBBBBBB':
    '[1-9]\\d{6,}'}
FULL_PART_FORMATS = {'pep440_pycalver':
    '{year}{month:02}.{BID}{pep440_tag}', 'pycalver':
    'v{year}{month:02}.{bid}{release}', 'calver': 'v{year}{month:02}',
    'semver': '{MAJOR}.{MINOR}.{PATCH}', 'release_tag': '{tag}', 'build':
    '.{bid}', 'month': '{month:02}', 'build_no': '{bid}', 'iso_week':
    '{iso_week:02}', 'us_week': '{us_week:02}', 'dom': '{dom:02}', 'doy':
    '{doy:03}', 'pep440_version': '{year}{month:02}.{BID}{pep440_tag}',
    'version': 'v{year}{month:02}.{bid}{release}'}
PART_FORMATS = {'major': '[0-9]+', 'minor': '[0-9]{3,}', 'patch':
    '[0-9]{3,}', 'bid': '[0-9]{4,}', 'MAJOR': '[0-9]+', 'MINOR': '[0-9]+',
    'MM': '[0-9]{2,}', 'MMM': '[0-9]{3,}', 'MMMM': '[0-9]{4,}', 'MMMMM':
    '[0-9]{5,}', 'MMMMMM': '[0-9]{6,}', 'MMMMMMM': '[0-9]{7,}', 'PATCH':
    '[0-9]+', 'PP': '[0-9]{2,}', 'PPP': '[0-9]{3,}', 'PPPP': '[0-9]{4,}',
    'PPPPP': '[0-9]{5,}', 'PPPPPP': '[0-9]{6,}', 'PPPPPPP': '[0-9]{7,}',
    'BID': '[1-9][0-9]*', 'BB': '[1-9][0-9]{1,}', 'BBB': '[1-9][0-9]{2,}',
    'BBBB': '[1-9][0-9]{3,}', 'BBBBB': '[1-9][0-9]{4,}', 'BBBBBB':
    '[1-9][0-9]{5,}', 'BBBBBBB': '[1-9][0-9]{6,}'}


def _replace_pattern_parts(pattern):
    for part_name, part_pattern in PART_PATTERNS.items():
        named_part_pattern = '(?P<{0}>{1})'.format(part_name, part_pattern)
        placeholder = '\\{' + part_name + '\\}'
        pattern = pattern.replace(placeholder, named_part_pattern)
    return pattern


def _compile_pattern(pattern):
    for char, escaped in PATTERN_ESCAPES:
        pattern = pattern.replace(char, escaped)
    return _replace_pattern_parts(pattern)


def compile_pattern(pattern):
    pattern_str = _compile_pattern(pattern)
    return re.compile(pattern_str)


def _init_composite_patterns():
    for part_name, part_pattern in COMPOSITE_PART_PATTERNS.items():
        part_pattern = part_pattern.replace('{', '\\{').replace('}', '\\}')
        pattern_str = _replace_pattern_parts(part_pattern)
        PART_PATTERNS[part_name] = pattern_str


_init_composite_patterns()
