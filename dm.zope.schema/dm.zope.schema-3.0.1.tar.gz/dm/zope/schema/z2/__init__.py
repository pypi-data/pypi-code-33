# Copyright (C) 2011-2018 by Dr. Dieter Maurer <dieter@handshake.de>
"""Zope 2 support"""
from sys import version_info

# Python version compatibility
python_major_version = version_info.major

#  Zope version compatibility
try:
  from App.version_txt import getZopeVersion
  zope_major_version = getZopeVersion()[0]
except ImportError: zope_major_version = 4 # work aroung Zope [4] beta bug
