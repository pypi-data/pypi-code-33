#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright (C) 2019 Christoph Fink, University of Helsinki
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, see <http://www.gnu.org/licenses/>.

from .SentimentIdentifier import (
    SentimentIdentifier
)

__all__ = [
    "SentimentIdentifier",
    "identifySentiment",
    "__name__",
    "__version__"
]

name = "webis"  # noqa: F401
__name__ = name

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def identifySentiment(tweets):
    with SentimentIdentifier() as s:
        tweets = s.identifySentiment(tweets)

    return tweets
