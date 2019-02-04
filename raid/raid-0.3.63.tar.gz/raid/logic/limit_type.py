# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

from enum import Enum

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class LimitType(Enum):
    EPOCHS = "EPOCHS"
    SECONDS = "SECONDS"
    MINUTES = "MINUTES"
    HOURS = "HOURS"
