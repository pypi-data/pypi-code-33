# encoding=UTF-8
# Copyright 2016 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import unicode_literals
from functools import partial, reduce
import unicodedata
import re

STOPS = {'a' 'an', 'and', 'as', 'at', 'be', 'by', 'etc', 'for',
         'from', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'of', 'on',
         'or', 'so', 'that', 'the', 'to'}

splitwords = re.compile(r'[^a-z0-9]+').split
remove_apostrophies = partial(
    re.compile(r"(?<=[a-z0-9])[’'](?=[a-z0-9])").sub, '')
remove_number_separators = partial(re.compile('(?<=\d),(?=\d\d\d)').sub, '')


def _agg_words(acc, newword, limit):
    """
    :param acc: accumulator tuple of (running_total_length, words)
    :param newword: a new word to add to `acc` if it fits within the length
                    limit
    """
    running_total, words = acc
    # Add 1 char for the separator
    wordlen = len(newword) + 1
    if running_total + wordlen <= limit:
        words.append(newword)
        running_total += wordlen
    return (running_total, words)


def remove_accents(s,
                   normalize=unicodedata.normalize,
                   combining=unicodedata.combining):
    """
    Return ``s`` with all non-ascii characters stripped
    """
    return ''.join(c for c in normalize('NFD', s) if not combining(c))


def remove_stops(words, stops):
    new = [w for w in words if w not in stops]
    return new or words


def truncate_on_boundaries(words, maxlen):
    new = reduce(partial(_agg_words, limit=maxlen), words, (0, []))
    if new:
        return new[1]
    return words[0][:maxlen]


def slugify(s,
            maxlen=None,
            stops=STOPS,
            separator='-',
            splitwords=splitwords,
            remove_apostrophies=remove_apostrophies):

    s = s.lower()
    s = remove_apostrophies(s)
    s = remove_number_separators(s)
    s = remove_accents(s)
    words = splitwords(s)
    words = [w for w in words if w]
    if stops:
        words = remove_stops(words, stops)

    if maxlen:
        words = truncate_on_boundaries(words, maxlen)

    return separator.join(words)
