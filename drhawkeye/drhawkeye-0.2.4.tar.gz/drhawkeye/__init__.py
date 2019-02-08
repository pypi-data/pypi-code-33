# -*- coding: utf-8 -*-
import os

__author__ = """Micah Sandusky"""
__email__ = 'micah.sandusky@ars.usda.gov'
__version__ = '0.2.4'

__core_config__ = os.path.abspath(os.path.dirname(__file__) + '/CoreConfig.ini')
__recipes__ = os.path.abspath(os.path.dirname(__file__) + '/recipes.ini')
__config_checkers__ = 'checkers'

from . import checkers
from . import framework
from . import health_check
