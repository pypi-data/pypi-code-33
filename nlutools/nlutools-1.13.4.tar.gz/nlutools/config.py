import os
from os import path

#baseDir = os.path.dirname(path.dirname(__file__))
baseDir = os.path.dirname(__file__)

def readModuleMapping(mapFile):
    with open(mapFile,'r') as f:
        return {item[0]:item[1] for item in \
                        (line.strip().split('=') for line in f.readlines() \
                        if line.strip() and not line.strip().startswith('#'))}

#mapConf = readModuleMapping('../config/module_mapping.txt')
mapConf = readModuleMapping(baseDir+'/config/module_map_url.txt')
supportConf = readModuleMapping(baseDir+'/config/support_conf.txt')
