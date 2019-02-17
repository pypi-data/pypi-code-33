#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Pacifica Downloader Module.

The primary exposed class is the `Downloader` class. There are two
internal classes to pull the metadata required to interact with the
Cartd service.
"""
from __future__ import absolute_import
from .downloader import Downloader

__all__ = ['Downloader']
