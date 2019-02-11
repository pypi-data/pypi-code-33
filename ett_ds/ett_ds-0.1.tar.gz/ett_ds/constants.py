#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Emerging Technologies Team Core Library housing ENUM lists

Contains functions that focus on cleaning data
"""

from enum import Enum

__author__ = "Kevin Thomas Bradley"
__copyright__ = "Copyright 2019, United Nations OICT PSGD ETT"
__credits__ = ["Kevin Bradley", "Yihan Bao", "Praneeth Nooli"]
__date__ = "07 February 2019"
__version__ = "0.1"
__maintainer__ = "Kevin Thomas Bradley"
__email__ = "bradleyk@un.org"
__status__ = "Development"

# List of encoding types
class Encoding(Enum):
    LATIN_1 = "latin1"

# List of job processing types
class JobType(Enum):
    BATCH = "BATCH",
    SINGLE = "SINGLE"

# List of regular expressions
class RegexFilter(Enum):
    NON_ALPHA_NUMERIC = "[^\w\s]",      # ^ NOT, \w WORDS, \s WHITESPACE
    DIGITS_ONLY = "[\d]"                # \d DIGITS

# KV list of languages and ISO code
class Language(Enum):
    ENGLISH = "en_US"