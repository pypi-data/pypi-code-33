#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 12:17:17 2018

@author: Sven Serneels, Ponalytics
"""

__name__ = "sprm"
__author__ = "Sven Serneels"
__license__ = "GNU"
__version__ = "0.1.16"
__date__ = "2019-01-26"

from ._m_support_functions import *
from .robcent import robcent
from .sprm import snipls,sprm
from .rm import *

import numpy as np
import scipy.stats as sps
from statsmodels import robust as srs
import pandas as ps
from scipy.stats import norm, chi2
import copy



