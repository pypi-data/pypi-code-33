# -*- coding: UTF-8 -*-
# $Id: gmconst.py 4238 2016-09-27 11:27:39Z jeanluc $
#
# Copyright 2016 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
Created on 4 nov. 2015

@author: jeanluc
'''
from collections import defaultdict
verbose= 0

# KEEP_TEMP = "$$$"  #0

# dictionnaire des valeurs par defaut des connections
# pour les atomes, la valeur est -1
# pour les elements de structure, la valeur est 0
defaultConnect = defaultdict(lambda:-1)
defaultConnect.update({
#     "H": 0,
#     "D": 0,
    "iso": 0,
    "iso1": 0,
    "iso2": 0,
    "isomer": 0,
    "isomer(1)": 0,
    "isomer(2)": 0,
    "chi": 0,
    "chi1": 0,
    "chi2": 0,
    "chiral": 0,
    "chiral(1)": 0,
    "chiral(2)": 0,
    
    "ccl1": 0,
    "ccl2": 0,
    "ccl3": 0,
    "ccl4": 0,
    "ccl5": 0,
    "ccl6": 0,
    "ccl7": 0,
    "ccl8": 0,
    "ccl9": 0,
    "ccl10": 0,
    "ccl11": 0,
    "ccl12": 0,
    
    "cycle(1)": 0,
    "cycle(2)": 0,
    "cycle(3)": 0,
    "cycle(4)": 0,
    "cycle(5)": 0,
    "cycle(6)": 0,
    "cycle(7)": 0,
    "cycle(8)": 0,
    "cycle(9)": 0,
    "cycle(10)": 0,
    "cycle(11)": 0,
    "cycle(12)": 0,
    
    "qp1": 0,
    "qp2": 0,
    "qp3": 0,
    "qp4": 0,
    
    "charge(+1)": 0,
    "charge(+2)": 0,
    "charge(+3)": 0,
    "charge(+4)": 0,
    
    "qm1": 0,
    "qm2": 0,
    "qm3": 0,
    "qm4": 0,
    
    "charge(-1)": 0,
    "charge(-2)": 0,
    "charge(-3)": 0,
    "charge(-4)": 0,
    })

    