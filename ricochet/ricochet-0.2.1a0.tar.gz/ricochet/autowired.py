#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Type


class Autowired:
    """
    Marks a field that is to be autowired in.

    >>> foo: Autowired(int)
    >>> bar: Autowired()
    """

    def __init__(self, type: Type = Any):
        self.type = type
