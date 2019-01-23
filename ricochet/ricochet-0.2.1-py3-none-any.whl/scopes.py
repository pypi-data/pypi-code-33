#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Objectlet scope.
"""
import enum


class Scope(enum.Enum):
    """Describes the scope of an objectlet."""

    #: Singleton object
    SINGLETON = enum.auto()
    #: Base object that would be used to generate prototypes.
    PROTOTYPE = enum.auto()
