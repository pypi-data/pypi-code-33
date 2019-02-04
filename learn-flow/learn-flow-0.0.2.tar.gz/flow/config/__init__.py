# -*- coding: utf-8 -*-
"""
Package config
----------------------
A unified configuration tool used by tripod to load and manage system configuration and files.
It loads configuration files from pre-defined paths in a hierarchical precedence order.
The hierarchical order is defined on the object attribute `config.search_paths`.
"""
from .config import Config
