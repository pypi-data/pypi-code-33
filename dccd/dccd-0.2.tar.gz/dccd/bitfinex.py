#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" 
Bitfinex exchange class to download data. 

"""

# Import built-in packages
import os
import pathlib
import time

# Import local packages
from dccd.time_tools import TimeTools
from dccd.exchange import ImportDataCryptoCurrencies

__all__ = ['FromBitfinex']

class FromBitfinex(ImportDataCryptoCurrencies):