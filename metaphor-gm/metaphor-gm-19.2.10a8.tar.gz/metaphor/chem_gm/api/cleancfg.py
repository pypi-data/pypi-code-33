#-*- coding: ISO-8859-15 -*-
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
Created on 17 juin 2015

@author: jeanluc

Cet utilitaire est destiné à remettre le fichier graphùachine.cfg dans l'étét
de départ en vue de la création des distributions
'''

import sys, os
try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser
from ...nntoolbox.configparsertoolbox import defaultedConfigParser

def setto(conf, section, option, value, docreate=False):
    if docreate and not conf.has_option(section, option):
        conf.set(section, option, value)
    elif conf.get(section, option) != value:
        conf.set(section, option, value)
        return True
    return False

if __name__ == '__main__':
    try:
        conffile = os.path.join(sys.argv[1], 'graphmachine.cfg')
    except:
        conffile = os.path.join('graphic_interface', 'graphmachine.cfg')
    conffile = os.path.abspath(conffile)
    conf = SafeConfigParser()
    with open(conffile, "r") as ff:
        conf.readfp(ff)
        setto(conf, "usage", "modeldir", "")
        
        setto(conf, "private", "debugfile", "", True)
        setto(conf, "private", "keeptemp", "", True)
        
        setto(conf, "display", "jacobian", "False", True)
        setto(conf, "display", "actualepochs", "False", True)
        setto(conf, "display", "actualhidden", "False", True)
        setto(conf, "display", "meancorrel", "False", True)
        setto(conf, "display", "trace", "False", True)
        setto(conf, "display", "eigenmin", "False", True)
        setto(conf, "display", "eigenmax", "False", True)
        setto(conf, "display", "determinant", "False", True)
        setto(conf, "display", "r2adjust", "False", True)
        setto(conf, "display", "stddevbiasless", "False", True)
    
    with open(conffile, "w") as ff:
        conf.write(ff)
    #print "done"


def clearConnect(dico, atoms):
    res = {}
#    for key, val in dico.iteritems():
    for key, val in dico.items():
        if key in atoms:
            res[key] = val
        elif val:
            res[key] = val
    return res
    
def defaultGMCfg(excluded=[]):   
    config = defaultedConfigParser() 
    sectionlist = ("general", "model", "connectivity", "training", "private")
    for section in sectionlist:
        if not section in excluded:
            config.add_section(section)
    config.set("general", "fullhydrogen", "False")
    config.set("general", "simpledispersion", "False")
    config.set("general", "verbose", "0")
    
    config.set("model", "compiler", "")
    config.set("model", "hidden", "0")
    config.set("model", "mergeisochiral", "False")
    config.set("model", "mol1", "True")
    config.set("model", "isomeric_algo", "1")
#     config.set("model", "max neuron", "15")
#     config.set("model", "hid denmax", "20")
    
    config.set("private", "keeptemp", "")
    config.set("private", "compactness", "3")
    config.set("private", "moduletype", "dll")
    return config 
   