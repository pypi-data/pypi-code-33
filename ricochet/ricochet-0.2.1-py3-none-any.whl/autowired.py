#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import typing


class Autowired:
    """
    Marks a class as being autowired.

        >>> foo: Autowired[int]
        >>> bar: Autowired
    """

    @classmethod
    def __class_getitem__(cls, item):
        """
        If we are type checking, then use the type hint directly as the type, but if we are
        running then we need to retain the class as the annotation or it will fail to be detected.
        """
        return typing.TYPE_CHECKING and item or cls
