# -*- coding: utf-8 -*-

"""
<Description>
"""

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"
__version__ = "0.3.61"

from raid.logic.trainer import Trainer
from raid.data.interface.i_dataset import IDataset
from raid.logic.engine import Engine

# ===================================================================================================
# Execution Aliases.
# ===================================================================================================

run = Engine.execute
execute = Engine.execute
start = Engine.execute
